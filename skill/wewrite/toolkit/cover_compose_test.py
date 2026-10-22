import tempfile, unittest
from pathlib import Path
from PIL import Image
from cover_compose import compose_cover


class ComposeTest(unittest.TestCase):
    def test_regions_and_ratios(self):
        d = Path(tempfile.mkdtemp())
        Image.new("RGB", (2350, 1000), (255, 0, 0)).save(d / "w.png")
        Image.new("RGB", (1000, 1000), (0, 0, 255)).save(d / "s.png")
        out, cw, cs = compose_cover(str(d / "w.png"), str(d / "s.png"), str(d / "c.jpg"))
        im = Image.open(out)
        W, H = im.size
        self.assertEqual((W, H), (2350, 2000))
        x1, y1, x2, y2 = map(float, cw.split("_"))
        self.assertAlmostEqual((x2 - x1) * W / ((y2 - y1) * H), 2.35, places=3)
        x1, y1, x2, y2 = map(float, cs.split("_"))
        self.assertAlmostEqual((x2 - x1) * W, (y2 - y1) * H, delta=1)
        r, g, b = im.getpixel((int((x1 + x2) / 2 * W), int((y1 + y2) / 2 * H)))
        self.assertGreater(b, 200); self.assertLess(r, 60)
        r, g, b = im.getpixel((W // 2, H // 4))
        self.assertGreater(r, 200)

    def test_publisher_payload(self):
        import publisher
        captured = {}
        class R:
            def json(self): return {"media_id": "m"}
        def fake_post(url, params=None, data=None, headers=None):
            import json; captured.update(json.loads(data)); return R()
        orig = publisher.requests.post; publisher.requests.post = fake_post
        try:
            publisher.create_draft("t", "T", "<p>x</p>", "d", thumb_media_id="th",
                                   pic_crop_235_1="0_0_1_0.5", pic_crop_1_1="0_0.5_0.425532_1")
        finally:
            publisher.requests.post = orig
        a = captured["articles"][0]
        self.assertEqual(a["pic_crop_1_1"], "0_0.5_0.425532_1")
        self.assertEqual(a["pic_crop_235_1"], "0_0_1_0.5")


if __name__ == "__main__":
    unittest.main()
