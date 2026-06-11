# AltStore Source (auto-updating)

A self-hosted AltStore/SideStore source. You edit `config.json`; a GitHub Action
regenerates `source.json` on a schedule and commits it. GitHub Pages serves it.

## Setup

1. Create a new public GitHub repo and drop these files in (keep the structure,
   including `.github/workflows/`).
2. Edit `config.json` — set your source `name`/`identifier` and list your apps.
   - **`releases` mode**: point `repo` at the GitHub repo whose Releases hold the
     `.ipa` assets. Versions are pulled automatically, newest first.
   - **`static` mode**: hand-write the `versions` array. Use this if the IPAs are
     hosted as plain files (e.g. on a Pages site) rather than Release assets.
3. Run it once locally to sanity-check: `python scripts/generate_source.py`
   (it reads `config.json`, writes `source.json`).
4. Push. Then **Settings → Pages → Deploy from branch → main / root**.
5. Subscribe in AltStore:
   `https://<your-username>.github.io/<repo>/source.json`

## How updates flow

AltStore polls **your** `source.json` and treats `versions[0]` as the latest. In
`releases` mode, when upstream cuts a new release the Action rebuilds the file and
your subscribers get the update notification automatically — no manual edits.

## Notes

- The Action runs every 6 hours; change the `cron` in
  `.github/workflows/update-source.yml` to taste, or trigger it manually from the
  Actions tab (workflow_dispatch).
- `bundleIdentifier`, `name`, `iconURL`, and description come from `config.json` —
  GitHub Releases don't carry that metadata, so set it once per app.
- `tintColor` is a hex string with no `#`.
