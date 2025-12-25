# Troubleshooting

## "Unable to import DaVinciResolveScript"
- Ensure `RESOLVE_SCRIPT_API` points to the Resolve scripting modules directory.
- Confirm the module is readable by your Python interpreter.

## No active project/timeline
- Open a project and select the timeline in Resolve before running the tool.

## Missing render settings
- The Resolve API does not expose every render knob; the Delivery Spec tool will generate a manifest/checklist instead.

## UI cannot connect to Resolve
- The UI runs externally. Ensure the same Python can import `DaVinciResolveScript`.
- Consider launching the UI from a terminal where `RESOLVE_SCRIPT_API` is exported.
