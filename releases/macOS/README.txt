================================================================================
                    RESOLVE PRODUCTION SUITE v0.3.16
================================================================================

10 Workflow Automation Tools for DaVinci Resolve

================================================================================
                         HOW TO INSTALL
================================================================================

  1. Double-click "DOUBLE_CLICK_ME.command"
  2. If you see "unidentified developer": Right-click > Open > Open
  3. Python installs automatically if needed
  4. Select "Install" from the menu
  5. Done! A desktop shortcut is created.


================================================================================
                          HOW TO USE
================================================================================

  1. Open DaVinci Resolve (must be running first!)
  2. Double-click "Resolve Production Suite.command" on your Desktop
  3. Click "Connect Resolve" button
  4. Select your project and timeline
  5. Choose a tool, click "Run Tool"

That's it! The app auto-detects Resolve - no configuration needed.

SHORTCUT MISSING? Run this in Terminal:
  ./resolve-suite shortcut


================================================================================
                          THE 10 TOOLS
================================================================================

 1. Revision Resolver      - Replace assets across all timelines
 2. Relink Across Projects - Update assets across multiple projects
 3. Smart Reframer         - Convert 16:9 to 9:16, 1:1, etc.
 4. Caption Layout         - Verify captions in safe zones
 5. Feedback Compiler      - Convert feedback to timeline markers
 6. Timeline Normalizer    - Check FPS, resolution, disabled clips
 7. Component Graphics     - Manage reusable graphics library
 8. Delivery Spec Enforcer - Validate YouTube/Vimeo render settings
 9. Change Impact Analyzer - Compare timeline versions
10. Brand Drift Detector   - Audit brand guideline compliance

See docs/USER_GUIDE.md for detailed documentation on each tool.


================================================================================
                       TROUBLESHOOTING
================================================================================

"Resolve not connected"
  -> Make sure DaVinci Resolve is RUNNING before launching this app

"unidentified developer" warning
  -> Right-click > Open > Open

"permission denied"
  -> Run: chmod +x DOUBLE_CLICK_ME.command

Desktop shortcut missing
  -> Run: ./resolve-suite shortcut


================================================================================
                          SUPPORT
================================================================================

Email: contactmukundthiru@gmail.com
Docs:  See the docs/ folder for complete documentation

================================================================================
