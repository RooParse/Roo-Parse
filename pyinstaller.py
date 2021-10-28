import PyInstaller.__main__

PyInstaller.__main__.run([
    'gui.py',
    '-y',
    '--windowed',
    '-F',  # standalone file
    '-n', 'RooParse'
])
