# Installation

## Linux (Primary)

### 1) Install Python dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pip install -e .[ui]
```

### 2) Enable Resolve scripting
DaVinci Resolve ships `DaVinciResolveScript.py` in its developer folder.

Common locations:
- `/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.py`
- `/opt/resolve/Developer/Scripting/Modules/DaVinciResolveScript.so`

Export the module path:
```bash
export RESOLVE_SCRIPT_API=/opt/resolve/Developer/Scripting/Modules
```

Optional (custom python paths):
```bash
export RPS_RESOLVE_PYTHON_PATHS=/opt/resolve/Developer/Scripting/Modules
```

### 3) Run CLI or UI
```bash
resolve-suite list
resolve-suite run t6_timeline_normalizer --options sample_data/options_t6.json
resolve-suite-ui
```

Standalone tool entrypoints (optional):
```bash
rps-t1-revision-resolver --options sample_data/options_t1.json
rps-t8-delivery-spec-enforcer --options sample_data/options_t8.json
```

## Windows (Secondary)
- Resolve scripting modules are typically located under:
  `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules`
- Set environment variables with PowerShell:
```powershell
setx RESOLVE_SCRIPT_API "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
```

## macOS (Secondary)
- Resolve scripting modules are typically located under:
  `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules`
- Export:
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
```

## Environment Variables
- `RESOLVE_SCRIPT_API`: path to Resolve scripting modules
- `RPS_HOME`: suite data home (default `~/.rps`)
- `RPS_LOGS`: log path
- `RPS_REPORTS`: report path
- `RPS_PRESETS`: presets path
- `RPS_PACKS`: packs path

## Resolve Free vs Studio
- Tools will run on Resolve Free, but optional analysis (face/saliency) and some codec settings require Studio.
- The suite never uploads media; all processing is local.
