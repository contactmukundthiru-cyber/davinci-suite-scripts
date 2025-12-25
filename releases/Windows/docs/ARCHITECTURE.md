# Architecture

## Core Engine (`core/`)
- `config.py`: configuration + paths
- `logging.py`: JSON lines + human logs
- `fs.py`: safe file IO + atomic writes
- `jsonschema.py`: pack validation
- `similarity.py`: mapping/lookup scoring
- `reports.py`: report objects + exporters
- `transactions.py`: dry-run + rollback metadata
- `packs.py`: schema-validated pack loaders
- `presets.py`: preset save/load utilities

## Resolve Integration (`resolve/`)
- `resolve_api.py`: robust wrapper around Resolve scripting API
- `limitations.py`: known API gaps and workarounds
- `navigation_helpers.py`: timeline navigation helpers

## Tools (`tools/`)
Each tool is independent but uses shared config, logging, and reports.

## UI (`ui/`)
PySide6 desktop app for Linux-first orchestration.

## Packs & Schemas (`schemas/`, `presets/`)
Pack formats are validated via JSON Schema before use.
