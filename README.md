# MediaWatch SA (draft)

A public register of South African media bias: by publication, writer and article, plus journalists' own public posts. Bias is recorded FOR or AGAINST named actors, never as left/right, and every finding quotes the exact line and links its source.

Status: **draft, work in progress.** Scores are provisional and not yet validated.

- `plan.md`: the plan
- `docs/METHODOLOGY.md`: scoring method
- `data/`: schema, registers and pilot findings

## Build and test locally (DEV)

```sh
python scripts/build_site.py          # writes the static site to _site/ (gitignored)
python -m http.server -d _site 8000   # optional local preview
pip install -r requirements.txt       # jsonschema + pytest, for checks only
python scripts/validate_schema.py     # schema check of the findings and registers
python -m pytest -q                   # site tests
```

The generator uses the Python standard library only. The site is not deployed: the live domain still shows the placeholder `index.html`. See `changes/RFC-CHG-MW-002.md`.
