#!/usr/bin/env bash

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


# purpose:  Read-only check: compare the third-party versions pinned in
#           get-kosit-xr with the latest upstream releases. Changes nothing.
#
# usage:    run from the XFakturist repo root
#               .claude/skills/update-kosit/check-versions.sh
#
# needs:    curl, jq

set -u

SCRIPT="get-kosit-xr"
MIN_AGE_DAYS=14

[ -f "$SCRIPT" ] || { echo "run from the XFakturist repo root ($SCRIPT not found)"; exit 1; }
for tool in curl jq; do
    command -v "$tool" >/dev/null 2>&1 || { echo "missing tool: $tool"; exit 1; }
done

GH="https://api.github.com/repos"
GL_TAGS="https://projekte.kosit.org/api/v4/projects/xrechnung%2Fxrechnung-visualization/repository/tags?per_page=30"
GL_RAW="https://projekte.kosit.org/xrechnung/xrechnung-visualization/-/raw"
FOP_ARCHIVE="https://archive.apache.org/dist/xmlgraphics/fop/binaries/"

# value of VAR="..." in get-kosit-xr
pin() { sed -n "s/^$1=\"\(.*\)\"$/\1/p" "$SCRIPT"; }

# newest stable GitHub release whose tag matches regex $2
# prints: tag <TAB> age in days <TAB> first asset name
gh_latest() {
    curl -sf "$GH/$1/releases?per_page=30" | jq -r --arg re "$2" '
        [ .[] | select((.prerelease or .draft) | not) | select(.tag_name | test($re)) ]
        | first // empty
        | "\(.tag_name)\t\(((now - (.published_at | fromdateiso8601)) / 86400) | floor)\t\(.assets[0].name // "")"'
}

# newest KoSIT GitLab tag of the form vYYYY-MM-DD; prints: tag <TAB> age in days
gl_latest() {
    curl -sf "$GL_TAGS" | jq -r '
        [ .[] | select(.name | test("^v[0-9]{4}-[0-9]{2}-[0-9]{2}$")) ]
        | first // empty
        | "\(.name)\t\(((now - ((.commit.created_at[0:19] + "Z") | fromdateiso8601)) / 86400) | floor)"'
}

row() {  # name, pinned, latest, age
    local status
    if [ -z "$3" ]; then
        status="LOOKUP FAILED"
    elif [ "$2" = "$3" ]; then
        status="current"
    elif [ -n "$4" ] && [ "$4" -lt "$MIN_AGE_DAYS" ]; then
        status="newer, but only $4 days old (wait)"
    else
        status="UPDATE AVAILABLE${4:+ ($4 days old)}"
    fi
    printf "%-40s %-12s %-12s %s\n" "$1" "$2" "${3:--}" "$status"
}

printf "%-40s %-12s %-12s %s\n" "VARIABLE" "PINNED" "LATEST" "STATUS"
printf "%-40s %-12s %-12s %s\n" "--------" "------" "------" "------"

# KoSIT validator
IFS=$'\t' read -r tag age _ <<< "$(gh_latest itplr-kosit/validator '^v[0-9]+\.[0-9]+\.[0-9]+$')"
row KOSIT_VALIDATOR_VERSION "$(pin KOSIT_VALIDATOR_VERSION)" "${tag#v}" "$age"

# KoSIT validator configuration (asset name carries the XRechnung standard)
IFS=$'\t' read -r tag age asset <<< "$(gh_latest itplr-kosit/validator-configuration-xrechnung '^v[0-9]{4}-[0-9]{2}-[0-9]{2}$')"
row KOSIT_VALIDATOR_CONFIGURATION_RELEASE "$(pin KOSIT_VALIDATOR_CONFIGURATION_RELEASE)" "${tag#v}" "$age"
standard=$(echo "$asset" | sed -n 's/^xrechnung-\([0-9.]*\)-validator-configuration-.*/\1/p')
row KOSIT_XRECHNUNG_STANDARD "$(pin KOSIT_XRECHNUNG_STANDARD)" "$standard" ""

# KoSIT visualisation (GitLab), plus the FOP version its build pins
IFS=$'\t' read -r vis_tag age <<< "$(gl_latest)"
row KOSIT_VISUALIZATION_VERSION "$(pin KOSIT_VISUALIZATION_VERSION)" "${vis_tag#v}" "$age"

# Saxon-HE: major versions are released in parallel, so pick by version number,
# not by date; prints: major-minor <TAB> age in days (major "" = any)
saxon_highest() {
    curl -sf "$GH/Saxonica/Saxon-HE/releases?per_page=30" | jq -r --arg major "$1" '
        [ .[] | select((.prerelease or .draft) | not)
          | (.tag_name | capture("^SaxonHE-?(?<a>[0-9]+)-(?<b>[0-9]+)$")) as $v
          | select($major == "" or $v.a == $major)
          | { v: [($v.a | tonumber), ($v.b | tonumber)], published_at } ]
        | max_by(.v) // empty
        | "\(.v[0])-\(.v[1])\t\(((now - (.published_at | fromdateiso8601)) / 86400) | floor)"'
}
saxon_pin=$(pin SAXON_RELEASE)
saxon_major=${saxon_pin%%-*}
IFS=$'\t' read -r saxon_latest age <<< "$(saxon_highest "$saxon_major")"
row SAXON_RELEASE "$saxon_pin" "$saxon_latest" "$age"
IFS=$'\t' read -r saxon_newest _ <<< "$(saxon_highest "")"
if [ -n "$saxon_newest" ] && [ "${saxon_newest%%-*}" != "$saxon_major" ]; then
    echo "  note: newer Saxon-HE major version exists: $saxon_newest (not adopted by default)"
fi

# Apache FOP: recommended = version pinned in the latest visualisation pom.xml
fop_kosit=""
[ -n "$vis_tag" ] && fop_kosit=$(curl -sf "$GL_RAW/$vis_tag/pom.xml" | sed -n 's:.*<fop.version>\(.*\)</fop.version>.*:\1:p' | head -1)
fop_newest=$(curl -sf "$FOP_ARCHIVE" | grep -o 'fop-[0-9][0-9.]*-bin\.zip' | sed 's/^fop-//; s/-bin\.zip$//' \
             | sort -u -t. -k1,1n -k2,2n -k3,3n | tail -1)
row "FOP_VERSION (as pinned by KoSIT)" "$(pin FOP_VERSION)" "$fop_kosit" ""
echo "  note: newest FOP on archive.apache.org: ${fop_newest:-lookup failed}"
