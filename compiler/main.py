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
        "filename",
        type=Path,
        help="suitable XLSX workbook or JSON file with invoice data",
    )
    args = parser.parse_args()

    fully_qualified_path = (
        Path(args.filename).resolve().parents[0] / Path(args.filename).name
    )
    if not fully_qualified_path.is_file():
        parser.error(f"file not found: {fully_qualified_path}")
    if not fully_qualified_path.suffix in [".xlsx", ".json"]:
        parser.error(f"file type not supported: {fully_qualified_path.suffix}")

    # configure logging
    logging.basicConfig(
        filename=fully_qualified_path.with_suffix(".log"),
        filemode="w",
        format="%(asctime)s - %(name)s:%(lineno)d [%(levelname)s] - %(message)s",
        level=logging.INFO,
    )

    xr_invoice = XRechnung()
    if fully_qualified_path.suffix == ".xlsx":
        xr_invoice.read_xlsx(fully_qualified_path)
    elif fully_qualified_path.suffix == ".json":
        xr_invoice.read_json(fully_qualified_path)

    xr_invoice.write_xrechnung(fully_qualified_path.with_suffix(".xml"), debug=False)


if __name__ == "__main__":
    main()
