"""Create placeholder photos (campus.jpg, gate.jpg) so the sample renders without private images."""
import os
from PIL import Image, ImageDraw
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photos'); os.makedirs(d, exist_ok=True)
for name, c in (('campus.jpg', (40, 70, 90)), ('gate.jpg', (70, 60, 50))):
    im = Image.new('RGB', (1600, 1000), c); dr = ImageDraw.Draw(im)
    for i in range(0, 1600, 80): dr.line([(i, 0), (i + 600, 1000)], fill=tuple(min(255, x + 30) for x in c), width=6)
    im.save(os.path.join(d, name), quality=88)
print('photos ->', d)
