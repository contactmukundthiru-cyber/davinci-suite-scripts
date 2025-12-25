# Demo Runner

The demo runner executes every tool in dry-run mode and writes reports.

```bash
python scripts/demo_runner.py
```

Outputs:
- Reports in `~/.rps/reports` (JSON/CSV/HTML)
- Sample task exports in `sample_data/`

To run a specific tool with a sample options file:
```bash
resolve-suite run t5_feedback_compiler --options sample_data/options_t5.json
```
