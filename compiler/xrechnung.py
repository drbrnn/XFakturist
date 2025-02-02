# Copyright  2024 - present  Dr Tim Brunne (Munich)
#
# This file is part of XFakturist, <https://github.com/drbrnn/XFakturist>.
#
# XFakturist is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# XFakturist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with XFakturist.  If not, see <http://www.gnu.org/licenses/>.


import base64
import copy
import datetime
import decimal
import json
import json5
import logging
import pandas as pd
import re
import xmltodict

from pathlib import Path


class XRechnung:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._json_file = Path(__file__).with_suffix(".json")
        self._keyword_pattern = re.compile(
            r"^xr\:[A-Za-z0-9\_]+|^fakturist\:[A-Za-z\-]+"
        )
        self._amount_keyword_pattern = re.compile(r"^xr\:[A-Za-z0-9\_]+_amount$")
        self._decimal_number_keyword_pattern = re.compile(
            r"^xr\:[A-Za-z0-9\_]+_amount$|^xr\:[A-Za-z0-9\_]+_price$|^xr\:[A-Za-z0-9\_]+_VAT_rate$"
        )

        # data obtained from spreadsheet or JSON file
        self._currency_id = None
        self._invoice = {}
        self._invoice_lines = []
        self._additional_document_references = []

        # data to be calculated
        self._tax_subtotals = []

        # final data compilation, a dictionary that can be exported as XML
        self._xrechnung = {}

        # get template file for `self._xrechnung`
        if self._json_file.exists:
            self._logger.info(
                f"instantiating XRechnung object with template {self._json_file}"
            )
            with open(self._json_file) as f:
                self._xrechnung_template = json5.load(f)
        else:
            self._logger.warning(f"instantiating XRechnung object without template")
            self._xrechnung_template = {}

    # ---------- ---------- private methods ---------- ----------

    def _encode_binary_object(self, fq_filename: Path) -> str:
        """Read binary file `fq_filename` and return the content as an encoded string.
        If file `fq_filename` does not exist, return `None`.
        """

        if fq_filename.is_file():
            with open(fq_filename, "rb") as attachment:
                binary_object = base64.b64encode(attachment.read()).decode("utf-8")
            self._logger.info(f" > embedding file {fq_filename}")
            return binary_object
        else:
            self._logger.info(f" > file {fq_filename} not found")
            return None

    def _read_xlsx_sheet_columns(
        self, sheet_data: pd.DataFrame, wd: Path = None
    ) -> list:
        """Function to loop the data columns of workbook sheets "InvoiceLines"
        and "AdditionalDocumentReferences", and, to return a Python list of
        invoice-line dictionaries and additional-document-reference
        dictionaries, respectively.
        """
        target = []
        value_columns = sheet_data.columns[
            pd.Series(sheet_data.columns.str.match("^Line_|^Document_"))
        ].to_list()

        # loop all value columns of the worksheet
        for column in value_columns:
            column_data_are_complete = (
                sheet_data[column].notna() | (sheet_data.Mandatory != 1)
            ).all()

            self._logger.info(f"reading '{column}'")
            column_data = sheet_data[column].copy()
            column_dict = column_data.loc[
                column_data.notna() | (sheet_data.Mandatory == 1)
            ].to_dict()

            # Is there is a filename of some file to embed as a binary object?
            if type(column_dict.get("fakturist:Filename", None)) == str:
                column_dict["xr:Attached_document"] = self._encode_binary_object(
                    wd / column_dict["fakturist:Filename"]
                )
                column_data_are_complete = (
                    column_dict["xr:Attached_document"] is not None
                ) and column_data_are_complete

            if column_data_are_complete:
                self._logger.info(f" > column data look acceptable")
                decimal.getcontext().rounding = decimal.ROUND_HALF_UP
                for k, v in column_dict.items():
                    if self._amount_keyword_pattern.match(k):
                        column_dict[k] = round(decimal.Decimal(v), 2)
                    elif self._decimal_number_keyword_pattern.match(k):
                        column_dict[k] = decimal.Decimal(v)
                    if type(v) == datetime.datetime:
                        column_dict[k] = v.date().isoformat()
                target.append(column_dict)
            else:
                self._logger.info(f" > worksheet column skipped as data are incomplete")

        return target

    def _harmonise_imported_data(self):
        """Method to cast the data type of numerical data to `decimal.Decimal`,
        and, the data of type `datetime.datetime` to ISO formatted date
        strings. This method affects private members `self._invoice` and
        `self._invoice_lines`.

        Invoice (line) monetary amounts are always rounded to two decimal places.
        Item price figures can have more that two decimal figures and should be
        represented by decimal numbers with at least two decimal figures.
        """

        decimal.getcontext().rounding = decimal.ROUND_HALF_UP

        amount_keyword_pattern = re.compile(r"^xr\:[A-Za-z0-9\_]+_amount$")
        price_keyword_pattern = re.compile(r"^xr\:[A-Za-z0-9\_]+_price$")
        other_decimal_keyword_pattern = re.compile(
            r"^xr\:[A-Za-z0-9\_]+_VAT_rate$|^xr\:[A-Za-z0-9\_]+_quantity$"
        )
        for d in [self._invoice] + self._invoice_lines:
            for k, v in d.items():
                if type(v) == datetime.datetime:
                    d[k] = v.date().isoformat()
                elif amount_keyword_pattern.match(k):
                    d[k] = round(decimal.Decimal(v), 2)
                elif price_keyword_pattern.match(k):
                    d[k] = decimal.Decimal(v)
                    if d[k].as_tuple().exponent > -2:
                        d[k] = round(d[k], 2)
                elif other_decimal_keyword_pattern.match(k):
                    d[k] = decimal.Decimal(v)

    def _calculate_tax_total(self):
        """From list of dictionaries `self._invoice_lines` determine the list of
        dictionaries `self._tax_subtotals`, and, add key 'xr:Invoice_total_VAT_amount'
        and its value to dictionary `self._invoice`.
        """

        # FIXME: consider case without VAT tax information in invoice lines

        tax_data = pd.DataFrame.from_records(self._invoice_lines)

        # introduce decimal number arithmetic and proper rounding of decimal figures,
        # according to the half-up convention (German: kaufmännisches Runden)
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        for c in ["xr:Invoice_line_net_amount"]:
            tax_data[c] = tax_data[c].apply(lambda x: round(decimal.Decimal(x), 2))

        tax_data.loc[
            tax_data["xr:Invoiced_item_VAT_rate"].isna(), "xr:Invoiced_item_VAT_rate"
        ] = decimal.Decimal("0")

        # for all VAT categories, compute the total taxable amount
        tax_subtotals = (
            tax_data.groupby(
                ["xr:Invoiced_item_VAT_category_code", "xr:Invoiced_item_VAT_rate"]
            )["xr:Invoice_line_net_amount"]
            .agg("sum")
            .to_frame()
            .reset_index()
            .rename(
                columns={
                    "xr:Invoiced_item_VAT_category_code": "xr:VAT_category_code",
                    "xr:Invoiced_item_VAT_rate": "xr:VAT_category_rate",
                    "xr:Invoice_line_net_amount": "xr:VAT_category_taxable_amount",
                }
            )
        )
        # for all VAT categories, calculate the tax amount and round down
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        tax_subtotals["xr:VAT_category_tax_amount"] = (
            tax_subtotals["xr:VAT_category_rate"]
            * tax_subtotals["xr:VAT_category_taxable_amount"]
            / 100
        ).apply(lambda x: round(x, 2))

        # calculate invoice total amounts
        sum_of_invoice_line_net_amounts = tax_subtotals[
            "xr:VAT_category_taxable_amount"
        ].sum()
        invoice_total_vat_amount = tax_subtotals["xr:VAT_category_tax_amount"].sum()

        assert type(sum_of_invoice_line_net_amounts) == decimal.Decimal
        assert type(invoice_total_vat_amount) == decimal.Decimal
        self._invoice.update(
            {
                "xr:Sum_of_Invoice_line_net_amount": sum_of_invoice_line_net_amounts,
                "xr:Invoice_total_VAT_amount": invoice_total_vat_amount,
            }
        )
        self._tax_subtotals = tax_subtotals.to_dict("records")

    def _calculate_monetary_total(self):

        assert "xr:Sum_of_Invoice_line_net_amount" in self._invoice
        assert "xr:Invoice_total_VAT_amount" in self._invoice

        # BT-106 Summe der Nettobeträge aller Rechnungspositionen
        sum_of_invoice_line_net_amounts = decimal.Decimal(
            self._invoice.get("xr:Sum_of_Invoice_line_net_amount")
        )
        # BT-107 Summe der Abschläge auf Dokumentenebene
        sum_of_allowances_on_document_level = decimal.Decimal(
            decimal.Decimal(
                self._invoice.get("xr:Sum_of_allowances_on_document_level", 0)
            )
        )
        # BT-109 Rechnungsgesamtbetrag ohne Umsatzsteuer
        invoice_total_amount_without_vat = (
            sum_of_invoice_line_net_amounts - sum_of_allowances_on_document_level
        )
        # BT-110 Gesamtbetrag der Rechnungsumsatzsteuer
        invoice_total_vat_amount = decimal.Decimal(
            self._invoice.get("xr:Invoice_total_VAT_amount")
        )
        # BT-112 Rechnungsgesamtbetrag einschließlich Umsatzsteuer
        invoice_total_amount_with_vat = (
            invoice_total_amount_without_vat + invoice_total_vat_amount
        )
        # BT-113 Vorauszahlungsbetrag
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
        paid_amount = round(decimal.Decimal(self._invoice.get("xr:Paid_amount", 0)), 2)

        # BT-115 Fälliger Zahlungsbetrag
        amount_due_for_payment = invoice_total_amount_with_vat - paid_amount

        self._invoice.update(
            {
                "xr:Invoice_total_amount_without_VAT": invoice_total_amount_without_vat,
                "xr:Invoice_total_amount_with_VAT": invoice_total_amount_with_vat,
                "xr:Paid_amount": paid_amount,
                "xr:Amount_due_for_payment": amount_due_for_payment,
            }
        )

    def _process_dict(self, target: dict, source: dict) -> list:
        """If value `target` of a tree node (a synonym for dictionary key) is
        itself a dictionary (i.e. a subtree), then call this method. This method
        loops all first-level subtree nodes (i.e. dictionary keys) of subtree
        (i.e. dictionary) `target`. The returned recursion-depths list is a
        concatenation of the recursion-depths lists of all dictionary values,
        but the the recursion depth of each list tuple is incremented.
        """

        recursion_depths = []
        for key in target.keys():
            recursion_depths.extend(self._process_node(target, key, source))
        for key in [key for key, val in target.items() if val is None]:
            del target[key]
        return (
            [(k, x, rd + 1) for (k, x, rd) in recursion_depths]
            if recursion_depths
            else []
        )

    def _process_list(self, target: list, source: dict) -> list:
        """If value `target` of a tree node (which is a dictionary key) is a list,
        then call this method. This method loops all items of list `target` as if
        it where a dictionary, the keys being the integer-valued list item indices.
        The returned recursion-depths list is simply the concatenation of the
        received recursion-depths lists of all list items.
        """

        recursion_depths = []
        for key, val in enumerate(target):
            recursion_depths.extend(self._process_node(target, key, source))
        return recursion_depths

    def _process_node(self, target: dict | list, key: str, source: dict) -> list:
        """A private method that is used recursively, to compile the invoice
        nested dictionary `self._xrechnung`, which represents the 'invoice tree'.

        The term 'tree node' is used synonymously for 'dictionary key'. To compile the
        invoice dictionary `self._xrechnung`, call this method with parameters
        `target=self._xrechnung`, `key='Invoice'` and `source=self._invoice`.
        """

        val = target[key]

        if key == "@currencyID":
            # multiple currencies in the same invoice are not supported
            target[key] = self._currency_id
            return [(key, True, 1)]

        elif type(val) == str:
            if self._keyword_pattern.match(val):
                # if `target[key]` looks like a keyword, the value of `target[key]`
                # in template (sub)dictionary (or list) `target` must be replaced
                if val in source.keys():
                    target[key] = str(source[val])
                    return [(key, True, 1)]
                else:
                    target[key] = None
                    return []
            else:
                # the template's value for `target[key]` remains in place
                return [(key, False, 1)]

        elif type(val) == dict:
            recursion_depths = self._process_dict(val, source)
            if (
                recursion_depths == [("cbc:ID", False, 3)]
                or target[key] == {}
                or pd.Series(target[key].keys()).str.match(r"^@[A-Za-z]+$").all()
            ):
                # remove sub-dictionary `target[key]` if,
                # (a) a node is similar to an unused 'PartyTaxScheme' XML node, or,
                # (b) a node has attributes but no (text) value
                target[key] = None
                return []
            else:
                return recursion_depths

        elif type(val) == list:
            if len(val) == 1 and key in [
                "cac:InvoiceLine",
                "cac:AdditionalDocumentReference",
                "cac:TaxSubtotal",
            ]:
                # set variable `source_dictionaries` depending on the value of `key`
                if key == "cac:InvoiceLine":
                    source_dictionaries = self._invoice_lines
                elif key == "cac:AdditionalDocumentReference":
                    source_dictionaries = self._additional_document_references
                elif key == "cac:TaxSubtotal":
                    source_dictionaries = self._tax_subtotals
                else:
                    source_dictionaries = []

                # process all source dictionaries and build the list of items
                recursion_depths = []
                for source_dict in source_dictionaries:
                    list_item = copy.deepcopy(val[0])
                    recursion_depths.extend(self._process_dict(list_item, source_dict))
                    target[key].append(list_item)
                del target[key][0]

            else:  # all other lists
                recursion_depths = self._process_list(val, source)

            target[key] = [v for v in target[key] if v is not None]
            return recursion_depths

    def _prepare_xrechnung(self) -> list:
        """Based on invoice data available in private data members `self._invoice`,
        `self._invoice_lines` and `self._additional_document_references`, compile
        nested dictionary `self._xrechnung`.

        This dictionary can immediately be converted into an XML dataset or dumped
        as a JSON file. This function returns a list of triples, each three-tuple
        representing an invoice-data item that was inserted into dictionary
        `self._xrechnung`.
        """

        self._logger.info("compiling nested XRechnung dictionary from invoice data")
        self._xrechnung = copy.deepcopy(self._xrechnung_template)
        # self._invoice.update({"fakturist:UUID": uuid.uuid4()})
        return self._process_node(self._xrechnung, "Invoice", self._invoice)

    # ---------- ---------- public methods ---------- ----------

    def read_xlsx(self, workbook_file: Path):
        """Obtain invoice data from an XLSX workbook file, which has the required
        format (see the corresponding template file).
        """

        self._invoice.clear()
        self._invoice_lines.clear()
        self._additional_document_references.clear()

        self._logger.info(f"reading invoice data workbook: {workbook_file}")
        wb = pd.read_excel(workbook_file, sheet_name=None)

        sheet_names = set(wb.keys())
        self._logger.info(f"workbook sheet names: {sheet_names}")
        assert sheet_names.issuperset({"Invoice", "InvoiceLines"})

        for sheet_name in sheet_names.intersection(
            ["Invoice", "InvoiceLines", "AdditionalDocumentReferences"]
        ):
            self._logger.info(f"parsing sheet '{sheet_name}'")
            assert "Keyword" in wb[sheet_name].columns
            assert "Mandatory" in wb[sheet_name].columns
            sheet_data = wb[sheet_name].copy()
            sheet_data.set_index("Keyword", inplace=True)

            # (1) general invoice data
            if sheet_name == "Invoice":
                assert "Value" in wb[sheet_name].columns
                sheet_data = sheet_data[sheet_data.Value.notna()]
                self._invoice = sheet_data["Value"].to_dict()
                self._currency_id = self._invoice.get("xr:Invoice_currency_code", "EUR")

            # (2) invoice lines
            elif sheet_name == "InvoiceLines":
                self._invoice_lines = self._read_xlsx_sheet_columns(sheet_data)

            # (3) additional document references
            elif sheet_name == "AdditionalDocumentReferences":
                self._additional_document_references = self._read_xlsx_sheet_columns(
                    sheet_data, workbook_file.parent
                )

        self._harmonise_imported_data()
        self._calculate_tax_total()
        self._calculate_monetary_total()

    def read_json(self, json_file: Path):
        """Obtain invoice data from a JSON file that has the required
        format (see the corresponding template file).
        """

        self._logger.info(f"reading invoice data file: {json_file}")
        self._invoice.clear()
        with open(json_file, "r", encoding="utf-8") as f:
            self._invoice = json.load(f)
            self._invoice = {k: v for k, v in self._invoice.items() if v is not None}

        # (1) invoice currency
        self._currency_id = self._invoice.get("xr:Invoice_currency_code", "EUR")

        # (2) invoice lines
        self._invoice_lines = [
            {k: v for k, v in invoice_line.items() if v is not None}
            for invoice_line in self._invoice.pop("InvoiceLines", [])
        ]
        self._logger.info(f"found {len(self._invoice_lines)} invoice line(s)")

        # (3) additional document references
        self._additional_document_references = [
            {k: v for k, v in adr.items() if v is not None}
            for adr in self._invoice.pop("AdditionalDocumentReferences", [])
        ]
        self._logger.info(
            f"found {len(self._additional_document_references)} reference(s)"
        )
        for adr in self._additional_document_references:
            # Is there is a filename of some file to embed as a binary object?
            if type(adr.get("fakturist:Filename", None)) == str:
                adr["xr:Attached_document"] = self._encode_binary_object(
                    json_file.parent / adr["fakturist:Filename"]
                )
                if adr["xr:Attached_document"] is None:
                    self._logger.info(f" > reference skipped as data are incomplete")
                    adr = None
        self._additional_document_references = [
            adr for adr in self._additional_document_references if adr is not None
        ]

        self._harmonise_imported_data()
        self._calculate_tax_total()
        self._calculate_monetary_total()

    def write_xrechnung(self, filename: Path, debug: bool = False):
        self._prepare_xrechnung()
        filename_json = filename.with_suffix(".xml.json")

        if debug or filename.suffix == ".json":
            self._logger.info(f"exporting JSON file: {filename_json}")
            with open(filename_json, "w", encoding="utf-8") as f:
                json.dump(self._xrechnung, f, ensure_ascii=False, indent=4)

        if filename.suffix == ".xml":
            self._logger.info(f"exporting XML invoice: {filename}")
            invoice_xml = xmltodict.unparse(
                self._xrechnung, encoding="utf-8", pretty=True
            )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(invoice_xml)
