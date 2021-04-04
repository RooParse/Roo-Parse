import PyInstaller.__main__

PyInstaller.__main__.run([
    'gui.py',
    '--windowed',
    '-F',  # standalone file
    '-n RooParse'  # name of the programme
])
