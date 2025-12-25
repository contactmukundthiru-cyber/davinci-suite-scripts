# Quickstart

1) Activate venv
```bash
source .venv/bin/activate
```

2) Generate sample packs
```bash
python scripts/generate_sample_packs.py
```

3) Run demo (dry-run)
```bash
python scripts/demo_runner.py
```

Optional: run health check
```bash
python scripts/health_check.py
```

4) Run a tool in Resolve
```bash
resolve-suite run t1_revision_resolver --options sample_data/options_t1.json
```

5) Open UI
```bash
resolve-suite-ui
```

Reports are stored by default in `~/.rps/reports`.
Presets are stored in `~/.rps/presets/<tool_id>`.
