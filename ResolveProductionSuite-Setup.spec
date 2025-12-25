# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/mukund-thiru/Davinci_Suite/installer.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/mukund-thiru/Davinci_Suite/VERSION', '.'), ('/home/mukund-thiru/Davinci_Suite/README.md', '.'), ('/home/mukund-thiru/Davinci_Suite/LICENSE', '.'), ('/home/mukund-thiru/Davinci_Suite/requirements.txt', '.'), ('/home/mukund-thiru/Davinci_Suite/pyproject.toml', '.'), ('/home/mukund-thiru/Davinci_Suite/core', 'core'), ('/home/mukund-thiru/Davinci_Suite/resolve', 'resolve'), ('/home/mukund-thiru/Davinci_Suite/tools', 'tools'), ('/home/mukund-thiru/Davinci_Suite/cli', 'cli'), ('/home/mukund-thiru/Davinci_Suite/ui', 'ui'), ('/home/mukund-thiru/Davinci_Suite/schemas', 'schemas'), ('/home/mukund-thiru/Davinci_Suite/presets', 'presets'), ('/home/mukund-thiru/Davinci_Suite/scripts', 'scripts'), ('/home/mukund-thiru/Davinci_Suite/sample_data', 'sample_data'), ('/home/mukund-thiru/Davinci_Suite/docs', 'docs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ResolveProductionSuite-Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
