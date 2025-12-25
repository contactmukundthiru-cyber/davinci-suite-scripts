# SmartReframer

Standalone commercial tool for DaVinci Resolve.

## What it does
Create social variants and guided reframe markers per format.

## Requirements
- Python 3.9+
- DaVinci Resolve (Studio or Free)
- Resolve scripting module configured

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure Resolve Scripting
Linux example:
```bash
export RESOLVE_SCRIPT_API=/opt/resolve/Developer/Scripting/Modules
```

## Run
```bash
python run_tool.py --options sample_data/options.json
```

Reports are written to `~/.rps/reports` by default.

## Limitations
- Resolve scripting cannot control every UI or render parameter.
- This tool produces reports and guided action lists where automation is limited.
