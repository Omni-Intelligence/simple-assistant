# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cross-platform-assistant.py'],
    pathex=[],
    binaries=[],
    datas=[('/var/www/html/python/assisstant/.venv/lib/python3.10/site-packages/speech_recognition', 'speech_recognition'), ('/var/www/html/python/assisstant/.venv/lib/python3.10/site-packages/gtts', 'gtts'), ('/var/www/html/python/assisstant/.venv/lib/python3.10/site-packages/pydub', 'pydub')],
    hiddenimports=['speech_recognition', 'gtts', 'gtts.lang', 'pydub', 'pydub.playback', 'pyaudio', 'pyautogui', 'playsound'],
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
    name='voice_assistant',
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
