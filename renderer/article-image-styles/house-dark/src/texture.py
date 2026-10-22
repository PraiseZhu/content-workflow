import numpy as np
from PIL import Image, ImageFilter

def gblur(a, sx, sy=None):
    sy = sx if sy is None else sy
    H, W = a.shape
    fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.fftfreq(W)[None, :]
    g = np.exp(-2*(np.pi**2)*((fx*sx)**2 + (fy*sy)**2))
    return np.real(np.fft.ifft2(np.fft.fft2(a)*g))

def norm(a): return (a - a.mean())/a.std()

def make(W, H, base=19.0, fine=3.2, mid=2.2, scratch=1.0, mottle=1.6, broad=0.8, seed=7, scale=1.0):
    """scale: px of our image per reference px / 3.68 (cover = 1.0)"""
    rng = np.random.default_rng(seed)
    s = scale
    t = np.zeros((H, W))
    t += fine * norm(gblur(rng.standard_normal((H, W)), 0.8*s))
    t += mid * norm(gblur(rng.standard_normal((H, W)), 3.0*s))
    t += scratch * norm(gblur(rng.standard_normal((H, W)), 14*s, 1.0*s))
    t += mottle * norm(gblur(rng.standard_normal((H, W)), 22*s))
    t += broad * norm(gblur(rng.standard_normal((H, W)), 160*s))
    img = np.clip(base + t, 0, 255)
    return img

def save(img, path):
    a = np.repeat(np.round(img)[..., None], 3, axis=2).astype('uint8')
    Image.fromarray(a).save(path)

def stats_arr(L, box):
    im = Image.fromarray(np.clip(L, 0, 255).astype('uint8')) if isinstance(L, np.ndarray) else L.convert('L')
    c = im.crop(box)
    a = np.asarray(c).astype(float)
    hp = a - np.asarray(c.filter(ImageFilter.GaussianBlur(4))).astype(float)
    lo = np.asarray(c.filter(ImageFilter.GaussianBlur(12))).astype(float)
    return a.mean(), a.std(), hp.std(), lo.std()
