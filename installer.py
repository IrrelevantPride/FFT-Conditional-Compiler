import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--name=FFT Conditional Compiler',
    '--icon=images\sword_icon.ico',
    '--windowed'
])