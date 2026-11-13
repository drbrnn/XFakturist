# XFakturist

Minimalist, offline XRechnung (EN 16931 / UBL 2.1) e-invoice generator.
Python compiler + Bash wrappers around the KoSIT validator/visualiser.
Licensed AGPL-3.0-only; every source file carries the copyright/AGPL header — keep it on new files.

## Layout
- `xr-compile` – Python entry point → `compiler/main.py` (argparse, logging to `<input>.log`)
- `compiler/xrechnung.py` – `XRechnung` class: reads XLSX/JSON, computes VAT subtotals and totals, fills the template, writes XML via `xmltodict.unparse`
- `compiler/xrechnung.json` – **JSON5** template of the UBL Invoice tree (comments allowed). Leaf values like `"xr:Invoice_number"` are placeholder keywords replaced from input data; unmatched keywords and empty subtrees are pruned
- `template.json` / `template.xlsx` – user-facing input templates (XLSX sheets: `Invoice`, `InvoiceLines`, `AdditionalDocumentReferences`; columns `Keyword`, `Mandatory`, `Value` / `Line_*` / `Document_*`)
- `xr-validate`, `xr-convert` – Bash wrappers for KoSIT validator and Saxon/FOP visualisation (HTML + PDF, `de`|`en`). `xr-convert` accepts UBL Invoice, UBL CreditNote and CII; XFakturist itself only generates UBL Invoices
- `get-kosit-xr` – downloads pinned KoSIT/Saxon/FOP versions into `kosit-xr/` (git-ignored, as is `downloads/`)

## Invariants — do not break
- **Element order in `compiler/xrechnung.json` is significant**: it must follow the UBL-Invoice-2.1 XSD sequence. Insert new elements at the XSD-correct position.
- Keyword names (`xr:*` for EN 16931 business terms, `fakturist:*` for tool-specific fields such as `fakturist:Filename`) must stay identical across `xrechnung.json`, `template.json` and `template.xlsx`.
- Template comments document BT/BG numbers in German; `##` = mandatory per EN 16931, `#` = mandatory per XRechnung. Keep this convention.
- Money: use `decimal.Decimal` with `ROUND_HALF_UP` (kaufmännisches Runden); amounts rounded to 2 places, prices keep ≥2 places. Never use floats for amounts.
- Keyword-suffix conventions drive typing: `*_amount`, `*_price`, `*_VAT_rate`, `*_quantity`.
- Single currency per invoice (`@currencyID` comes from `xr:Invoice_currency_code`).
- XLSX and JSON input paths must behave the same (e.g. a reference whose attachment file is missing is dropped in both).

## Python
- Code is Black-formatted; check with `black --check compiler/`.
- Python ≥ 3.10: `pandas`, `openpyxl`, `json5`, `xmltodict`.

## Shell scripts
- Must run on macOS (Bash 3.2, BSD tools) **and** Linux (GNU tools, various JREs); Linux JRE differences have caused bugs before. Avoid GNU-only flags and Bash 4+ features.
- Temporary files go in a per-run `mktemp -d` directory removed by an `EXIT` trap — never fixed paths in `/tmp` or `/var/tmp`.
- Quote path variables; invoice paths may contain spaces.
- Scripts locate `kosit-xr/` by resolving their own symlinks, so they may be symlinked into `$PATH`. Keep that resolution block.
- `xmllint` is optional; keep the regex fallback in `xr-convert`.
- To update the KoSIT/Saxon/FOP versions, follow the `/update-kosit` skill (`.claude/skills/update-kosit/`). In short: edit only the version variables at the top of `get-kosit-xr` and check that the archive layouts still match the `mv`/`ln` steps.

## Verifying changes
There is no test suite. Starting from the repo root, run the round trip in a scratch directory so outputs and `template.log` don't land in the repo:

    REPO=$(pwd); mkdir -p /tmp/xf && cd /tmp/xf && cp "$REPO/template.json" . \
      && "$REPO/xr-compile" template.json \
      && "$REPO/xr-validate" template.xml \
      && "$REPO/xr-convert" template.xml

- `xr-validate` / `xr-convert` need a Java JRE and `kosit-xr/` (run `./get-kosit-xr` first).
- Inspect `template.log` and `template_validation_report.html`. Also try `template.xlsx` if the XLSX path changed.
- Expected FOP noise, not bugs: `table-layout="auto"` not implemented, missing hyphenation pattern, `fo:region-before` overflow.
- Never commit generated `*.xml`, `*_validation_report.*` or `*_converted_*` files.

## Known issues (open FIXMEs — delete an entry once fixed)
- `get-kosit-xr`: downloads are not verified by checksum or signature.
- `XRechnung._calculate_tax_total`: invoice lines without VAT information are not handled.

## Docs and commits
- `README.md` (English) and `README_de.md` (German) are kept in sync — update both.
- Commit messages: one short lowercase sentence describing the change, e.g. "bug fix to improve Linux JRE compatibility".
