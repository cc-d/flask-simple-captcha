import unittest
import time
from unittest.mock import patch, Mock
from flask_simple_captcha import CAPTCHA
from PIL import Image
from flask_simple_captcha.config import DEFAULT_CONFIG
from flask import Flask


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.config = DEFAULT_CONFIG
        self.config['EXPIRE_MINUTES'] = 1
        self.captcha = CAPTCHA(self.config)
        self.app = Flask(__name__)

    def test_create(self):
        result = self.captcha.create()
        self.assertIn('img', result)
        self.assertIn('text', result)
        self.assertIn('hash', result)

    def test_verify_valid(self):
        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']
        self.assertTrue(self.captcha.verify(text, c_hash))

    def test_verify_invalid(self):
        result = self.captcha.create()
        text = 'invalid_text'
        c_hash = result['hash']
        self.assertFalse(self.captcha.verify(text, c_hash))

    def test_verify_duplicate(self):
        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']
        self.assertTrue(self.captcha.verify(text, c_hash))
        self.assertFalse(self.captcha.verify(text, c_hash))

    def test_captcha_html(self):
        captcha = {'img': 'example_img', 'hash': 'example_hash'}
        html = self.captcha.captcha_html(captcha)
        self.assertIn('example_img', html)
        self.assertIn('example_hash', html)

    def test_get_background(self):
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

    def test_init_app(self):
        with patch("flask.Flask") as MockFlask:
            mock_app = MockFlask()
            ret_app = self.captcha.init_app(mock_app)
            mock_app.jinja_env.globals.update.assert_called()
            self.assertEqual(ret_app, mock_app)

    def test_reversed_args(self):
        result = self.captcha.create()
        c_text = result['text']
        c_hash = result['hash']

        self.assertTrue(self.captcha.verify(c_hash, c_text))

    def test_jwt_expiration(self):
        # Creating a captcha with a very short expiration time
        self.config['EXPIRE_MINUTES'] = 0
        self.captcha = CAPTCHA(self.config)

        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']

        self.assertFalse(self.captcha.verify(result['text'], result['hash']))

        self.config['EXPIRE_MINUTES'] = 1
        self.captcha = CAPTCHA(self.config)
        result = self.captcha.create()
        self.assertTrue(self.captcha.verify(result['text'], result['hash']))


if __name__ == '__main__':
    unittest.main()
