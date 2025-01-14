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


import argparse
import logging

from pathlib import Path
from .xrechnung import XRechnung


def main() -> None:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename", type=Path, help="suitable XLSX workbook with invoice data"
    )
    args = parser.parse_args()

    wd = Path(args.filename).resolve().parents[0]

    # configure logging
    log_file = wd / Path(args.filename.name).with_suffix(".log")
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        format="%(asctime)s - %(name)s:%(lineno)d [%(levelname)s] - %(message)s",
        level=logging.INFO,
    )
    logger = logging.getLogger(Path(__file__).name)

    # invoice data spreadsheets
    workbook_file = wd / Path(args.filename.name).with_suffix(".xlsx")
    if not Path.is_file(workbook_file):
        logger.error(f"file not found: {workbook_file}")
        parser.error(f"file not found: {workbook_file}")

    xr_invoice = XRechnung()
    xr_invoice.read_excel(workbook_file)
    xr_invoice.write_xrechnung(args.filename.with_suffix(".xml"), debug=False)


if __name__ == "__main__":
    main()
