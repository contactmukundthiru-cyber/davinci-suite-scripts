# Standalone Scripts

Each tool can be sold/shipped as a standalone script in two forms:

1) Console entrypoints (installed via pip)
- `rps-t1-revision-resolver`
- `rps-t2-relink-across-projects`
- `rps-t3-smart-reframer`
- `rps-t4-caption-layout-protector`
- `rps-t5-feedback-compiler`
- `rps-t6-timeline-normalizer`
- `rps-t7-component-graphics`
- `rps-t8-delivery-spec-enforcer`
- `rps-t9-change-impact-analyzer`
- `rps-t10-brand-drift-detector`

Each entrypoint accepts:
- `--options <path>` JSON options
- `--output <dir>` report output directory
- `--dry-run` (no changes)

2) Standalone script files
- `standalone_scripts/` contains single-file wrappers for each tool.
- These can be shipped directly to clients who already installed the core package.

3) Standalone product bundles
- `products/<tool_id>/` contains a full self-contained bundle for each tool.
- Each bundle includes core modules, Resolve wrappers, schemas, samples, and its own README.

Example:
```bash
rps-t1-revision-resolver --options sample_data/options_t1.json
python standalone_scripts/t1_revision_resolver.py --options sample_data/options_t1.json
```
