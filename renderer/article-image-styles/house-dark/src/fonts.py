import os
F = os.path.join(os.environ.get('FONT_DIR', os.path.expanduser('~/.local/share/fonts')), 'misans')
FACES = ''.join(f"@font-face{{font-family:'MiSansW';font-weight:{w};src:url('file://{F}/MiSans-{n}.ttf')}}" for w, n in ((400,'Regular'),(500,'Medium'),(600,'Semibold'),(700,'Bold')))
