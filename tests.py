import unittest
import time
import jwt
import string
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock

from flask import Flask

from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

from flask_simple_captcha import CAPTCHA

from flask_simple_captcha.config import DEFAULT_CONFIG, EXPIRE_NORMALIZED
from flask_simple_captcha.utils import (
    jwtencrypt,
    jwtdecrypt,
    gen_captcha_text,
    exclude_similar_chars,
    CHARPOOL,
    hash_text,
)
from flask_simple_captcha.img import (
    convert_b64img,
    draw_lines,
    create_text_img,
)
from flask_simple_captcha.text import CaptchaFont, get_font, CAPTCHA_FONTS

_TESTTEXT = 'TestText'
_TESTKEY = 'TestKey'

app = Flask(__name__)


class TestConfig(unittest.TestCase):
    def test_expire_seconds_priority(self):
        config_with_both = {'EXPIRE_SECONDS': 600, 'EXPIRE_MINUTES': 10}
        expected_expire_normalized = (
            600  # Expecting EXPIRE_SECONDS to take priority
        )

        if 'EXPIRE_SECONDS' in config_with_both:
            expire_normalized = config_with_both['EXPIRE_SECONDS']
        elif 'EXPIRE_MINUTES' in config_with_both:
            expire_normalized = config_with_both['EXPIRE_MINUTES'] * 60
        else:
            expire_normalized = EXPIRE_NORMALIZED  # Or set a default value

        self.assertEqual(expire_normalized, expected_expire_normalized)

    def test_only_expire_minutes(self):
        config_with_minutes = {'EXPIRE_MINUTES': 10}
        expected_expire_normalized = 600  # 10 minutes in seconds

        if 'EXPIRE_SECONDS' in config_with_minutes:
            expire_normalized = config_with_minutes['EXPIRE_SECONDS']
        elif 'EXPIRE_MINUTES' in config_with_minutes:
            expire_normalized = config_with_minutes['EXPIRE_MINUTES'] * 60
        else:
            expire_normalized = EXPIRE_NORMALIZED  # Or set a default value

        self.assertEqual(expire_normalized, expected_expire_normalized)

    def test_no_expire_values(self):
        config_without_expire = {}
        expected_expire_normalized = (
            EXPIRE_NORMALIZED  # Assuming no default value is set
        )

        if 'EXPIRE_SECONDS' in config_without_expire:
            expire_normalized = config_without_expire['EXPIRE_SECONDS']
        elif 'EXPIRE_MINUTES' in config_without_expire:
            expire_normalized = config_without_expire['EXPIRE_MINUTES'] * 60
        else:
            expire_normalized = EXPIRE_NORMALIZED  # Or set a default value

        self.assertEqual(expire_normalized, expected_expire_normalized)

    def test_expire_minutes_without_expire_seconds(self):
        config = {'EXPIRE_MINUTES': 10}
        expected_expire_normalized = 600  # 10 minutes in seconds

        captcha = CAPTCHA(config)
        self.assertEqual(captcha.expire_secs, expected_expire_normalized)

    def test_config_with_expire_minutes_only(self):
        config_with_expire_minutes = {
            'SECRET_CAPTCHA_KEY': 'TestKey',
            'CAPTCHA_LENGTH': 6,
            'EXPIRE_MINUTES': 5,
        }
        captcha_instance = CAPTCHA(config_with_expire_minutes)
        self.assertEqual(captcha_instance.expire_secs, 300)


class TestImg(unittest.TestCase):
    def test_convert_b64img(self):
        img = Image.new('RGB', (60, 30), color=(73, 109, 137))
        b64image = convert_b64img(img)
        self.assertIsInstance(b64image, str)


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.config = DEFAULT_CONFIG
        self.config['EXPIRE_NORMALIZED'] = 60
        self.captcha = CAPTCHA(self.config)

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
        self.assertEqual(bg.size, (text_size[0], text_size[1]))

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
        self.config['EXPIRE_NORMALIZED'] = 0
        self.captcha = CAPTCHA(self.config)

        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']

        self.assertFalse(self.captcha.verify(result['text'], result['hash']))

        self.config['EXPIRE_NORMALIZED'] = 60
        self.captcha = CAPTCHA(self.config)
        result = self.captcha.create()
        self.assertTrue(self.captcha.verify(result['text'], result['hash']))

    def test_arg_order(self):
        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']

        self.assertTrue(self.captcha.verify(c_hash, text))

        result = self.captcha.create()
        text = result['text']
        c_hash = result['hash']
        self.assertTrue(self.captcha.verify(text, c_hash))

    def test_backwards_defaults(self):
        """ensures backward compatibility with v1.0 default assumptions"""
        for i in range(5):
            result = self.captcha.create()
            for c in result['text']:
                self.assertIn(c, string.ascii_uppercase)

    def test_expire_seconds(self):
        """ensures expire_seconds is set correctly"""
        del self.config['EXPIRE_NORMALIZED']
        self.config['EXPIRE_SECONDS'] = 100
        self.captcha = CAPTCHA(self.config)
        self.assertEqual(self.captcha.expire_secs, 100)

    @patch(
        'flask_simple_captcha.captcha_generation.DEFAULT_CONFIG',
        {'EXPIRE_SECONDS': 99},
    )
    def test_default_expire_seconds(self):
        conf = DEFAULT_CONFIG.copy()
        del conf['EXPIRE_NORMALIZED']
        del conf['EXPIRE_SECONDS']

        captcha = CAPTCHA(conf)
        self.assertEqual(captcha.expire_secs, 99)

    @patch('flask_simple_captcha.captcha_generation.CHARPOOL', 'Z')
    def test_charpool(self):
        conf = DEFAULT_CONFIG.copy()

        cap = CAPTCHA(conf)
        self.assertEqual(cap.characters, ('Z',))

    def test_charpool_in_config(self):
        conf = DEFAULT_CONFIG.copy()
        conf['CHARACTER_POOL'] = 'X'

        cap = CAPTCHA(conf)
        self.assertEqual(cap.characters, ('X',))

    def test_only_upper_false(self):
        conf = DEFAULT_CONFIG.copy()
        testchars = 'AaBb'
        conf['ONLY_UPPERCASE'] = False
        conf['CHARACTER_POOL'] = testchars

        cap = CAPTCHA(conf)
        for c in cap.characters:
            self.assertIn(c, testchars)

    def test_captcha_digits(self):
        conf = DEFAULT_CONFIG.copy()
        conf['CAPTCHA_DIGITS'] = True

        cap = CAPTCHA(conf)
        for c in ['2', '3', '4', '5', '6', '7', '8', '9']:
            self.assertIn(c, cap.characters)

    @patch('flask_simple_captcha.captcha_generation.jwtdecrypt')
    def test_decrypt_text_nomatch(self, mock_jwtdecrypt):
        mock_jwtdecrypt.return_value = 'afsddsgfewfewggwegfw'
        conf = DEFAULT_CONFIG.copy()
        cap = CAPTCHA(conf)
        cap.create()
        self.assertFalse(cap.verify('test', 'test'))


class TestCaptchaUtils(unittest.TestCase):
    def test_jwtencrypt(self):
        token = jwtencrypt(_TESTTEXT, _TESTKEY, expire_seconds=100)
        decoded = jwt.decode(token, _TESTKEY, algorithms=['HS256'])

        self.assertAlmostEqual(int(decoded['exp']), int(time.time() + 100))
        decrypted_text = jwtdecrypt(token, _TESTTEXT, _TESTKEY)
        self.assertEqual(decrypted_text, _TESTTEXT)

    def test_jwtdecrypt_valid_token(self):
        token = jwtencrypt(_TESTTEXT)
        decoded_text = jwtdecrypt(token, _TESTTEXT)
        self.assertEqual(decoded_text, _TESTTEXT)

    def test_jwtdecrypt_invalid_token(self):
        expired_token = jwtencrypt(_TESTTEXT, expire_seconds=-100)
        self.assertIsNone(jwtdecrypt(expired_token, _TESTTEXT))

        invalid_token = "invalid.token.here"
        self.assertIsNone(jwtdecrypt(invalid_token, _TESTTEXT))

    def test_exclude_similar_chars(self):
        self.assertEqual(exclude_similar_chars("oOlI1A"), "A")

    def test_gen_captcha_text(self):
        deftext = gen_captcha_text()

        for c in deftext:
            self.assertIn(c, CHARPOOL)
            self.assertTrue(c.upper() == c)
            self.assertTrue(c in string.ascii_uppercase)

        # LENGTH / Pool / Add Digits / Only Uppercase
        AaDigits_text = gen_captcha_text(
            length=500, charpool="Aa", add_digits=True, only_uppercase=True
        )

        aachars = tuple(set('A' + string.digits))

        self.assertTrue(AaDigits_text.isalnum())
        self.assertTrue(AaDigits_text.isupper())

        for c in AaDigits_text:
            self.assertIn(c, aachars)

        self.assertTrue(len(AaDigits_text) == 500)

        # only uppercase behaviour
        oa_text = gen_captcha_text(
            length=100, charpool='Aa', only_uppercase=False
        )
        for c in oa_text:
            self.assertIn(c, 'Aa')

        oa_text = gen_captcha_text(length=100, charpool='Aa')
        for c in oa_text:
            self.assertIn(c, 'Aa')

    def test_hashed_text(self):
        hashed_text = hash_text(_TESTTEXT, _TESTKEY)
        self.assertTrue(check_password_hash(hashed_text, _TESTKEY + _TESTTEXT))

    @patch('flask_simple_captcha.utils.jwt.decode')
    def test_no_hashed_text(self, mock_jwtdecode):
        mock_jwtdecode.return_value = {'not': 'in'}
        hashed_text = jwtdecrypt(_TESTTEXT, _TESTKEY)
        self.assertIsNone(hashed_text)

    @patch('flask_simple_captcha.utils.EXCHARS', 'abcd')
    def test_exclude_similar_chars(self):
        # pass fake args
        testset = {'a', 'b', 'c', 'd', 'e'}
        exchars = exclude_similar_chars(testset)
        self.assertEqual(exchars, {'e'})

        testlist = ['a', 'b', 'c', 'd', 'e']
        exchars = exclude_similar_chars(testlist)
        self.assertEqual(exchars, ['e'])


class TestText(unittest.TestCase):
    def setUp(self):
        self.fonts = CAPTCHA_FONTS

    def test_repr_format(self):
        _font = self.fonts[0]
        _name = _font.name

        font = CaptchaFont(self.fonts[0].path)
        self.assertEqual(repr(font), '<CaptchaFont %r>' % _name)

    def test_get_font(self):
        font = get_font('RobotoMono-Bold', self.fonts)
        self.assertIsInstance(font, CaptchaFont)

    def test_get_font_by_filename(self):
        font = get_font('RobotoMono-Bold.ttf', self.fonts)
        self.assertIsInstance(font, CaptchaFont)

    def test_get_font_by_path(self):
        font = get_font(self.fonts[0].path, self.fonts)
        self.assertIsInstance(font, CaptchaFont)

    def test_get_font_not_found(self):
        font = get_font('notfourqeqerfqwnd', self.fonts)
        self.assertIsNone(font)


class TestBackwardsCompatibleMethods(unittest.TestCase):
    def setUp(self):
        self.config = DEFAULT_CONFIG
        self.config['EXPIRE_NORMALIZED'] = 60
        self.captcha = CAPTCHA(self.config)

    @patch('flask_simple_captcha.captcha_generation.new_draw_lines')
    def test_draw_lines(self, mock_drawlines):
        self.captcha.draw_lines(Image.new('RGB', (100, 100)))
        mock_drawlines.assert_called_once_with(Image.new('RGB', (100, 100)))


if __name__ == '__main__':
    unittest.main()
