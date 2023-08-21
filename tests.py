import unittest
from flask_simple_captcha import CAPTCHA
from PIL import Image
from flask_simple_captcha.config import DEFAULT_CONFIG


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.config = DEFAULT_CONFIG
        self.captcha = CAPTCHA(self.config)

    def test_create(self):
        result = self.captcha.create()
        self.assertIn('img', result)
        self.assertIn('text', result)
        self.assertIn('hash', result)

    def test_verify_valid(self):
        result = self.captcha.create()
        token = result['hash']
        text = result['text']
        self.assertTrue(self.captcha.verify(token, text))

    def test_verify_invalid(self):
        result = self.captcha.create()
        token = result['hash']
        text = 'invalid_text'
        self.assertFalse(self.captcha.verify(token, text))

    def test_captcha_html(self):
        img = "example_b64_image"
        jwt_str = "example_jwt_str"
        html = self.captcha.captcha_html(img, jwt_str)
        self.assertIn(img, html)
        self.assertIn(jwt_str, html)

    def test_background(self):
        text_size = (50, 50)
        bg = self.captcha.get_background(text_size)
        self.assertEqual(
            bg.size, (int(text_size[0] * 1.25), int(text_size[1] * 1.5))
        )

    def test_convert_b64img(self):
        img = Image.new('RGB', (60, 30), color=(73, 109, 137))
        b64image = self.captcha.convert_b64img(img)
        self.assertIsInstance(b64image, str)

    def test_repr(self):
        repr_str = repr(self.captcha)
        self.assertIsInstance(repr_str, str)


if __name__ == '__main__':
    unittest.main()
