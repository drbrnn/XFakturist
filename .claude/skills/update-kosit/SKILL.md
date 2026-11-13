---
name: update-kosit
description: Check for new releases of the third-party software that get-kosit-xr downloads (KoSIT validator, validator configuration, visualisation, Saxon-HE, Apache FOP), propose updated version pins, then install and verify them.
---

# Updating the third-party versions in get-kosit-xr

1. Run `.claude/skills/update-kosit/check-versions.sh` from the repo root and show its table.
   If everything is current, say so and stop.

2. For each component with a newer release, read its release notes or changelog and summarise
   what changed, flagging security fixes. Then propose new pins using these rules:
   - Only releases that are at least 2 weeks old; no pre-releases or `-rc` tags.
   - Validator configuration: the zip name must match `KOSIT_XRECHNUNG_STANDARD`. If a new
     XRechnung standard appears, stop and ask; that is a bigger change than an update.
   - Validator: prefer the version the newest validator configuration says it was built against.
   - Saxon-HE: stay on the current major version unless KoSIT's visualisation build moves to a
     newer one. Mention a newer major version, but don't adopt it.
   - FOP: use the version pinned in the visualisation's `pom.xml` (`fop.version`) for the chosen tag.
   - Downloads must stay on archive.apache.org; dlcdn.apache.org only keeps the newest release.

   Sources: the URLs in the comment block of `get-kosit-xr`; release notes via
   `https://api.github.com/repos/<owner>/<repo>/releases/tags/<tag>`; the visualisation
   changelog at `https://projekte.kosit.org/xrechnung/xrechnung-visualization/-/raw/<tag>/CHANGELOG.md`.

3. Before editing, check that what the script expects is still there:
   - each download URL returns HTTP 200;
   - the Saxon zip contains `saxon-he-<major>.<minor>.jar`;
   - the visualisation archive still has `conf/`, `conf/fonts/`, `conf/fop.xconf`, `src/xsd/`
     and the five XSL files under `src/xsl/` that `xr-convert` uses
     (`ubl-invoice-xr.xsl`, `ubl-creditnote-xr.xsl`, `cii-xr.xsl`, `xrechnung-html.xsl`, `xr-pdf.xsl`).
   Download test files into the session scratchpad, not the repo.
   If the layout changed, propose matching changes to the `mv`/`ln` steps.

4. Show the proposed diff of `get-kosit-xr` and wait for approval.

5. After approval: move `kosit-xr/` to `kosit-xr.bak/`, run `./get-kosit-xr` from the repo root,
   then run the round trip from CLAUDE.md "Verifying changes". On failure, restore the backup
   and report.

6. On success, ask before deleting `kosit-xr.bak/`, and propose a commit message in the project's
   style, e.g. "upgrade to the <months year> versions of KoSIT software …". Never commit without
   being asked.
