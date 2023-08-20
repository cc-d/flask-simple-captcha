import unittest
from datetime import datetime, timedelta
from flask_simple_captcha import CaptchaHash, CAPTCHA, DEFAULT_CONFIG
from werkzeug.security import generate_password_hash
from flask_simple_captcha.captcha_generation import (
    CAPTCHA,
    DEFAULT_CONFIG,
    gen_captcha_key,
)
import unittest
from PIL import Image


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.captcha = CAPTCHA(DEFAULT_CONFIG)

    def test_create(self):
        caphash = self.captcha.create()

        # Check if the returned value is a CaptchaHash object
        self.assertIsInstance(caphash, CaptchaHash)

        self.assertEqual(len(caphash.text), DEFAULT_CONFIG['CAPTCHA_LENGTH'])

    def test_verify_valid(self):
        # Creating a new CAPTCHA
        caphash = self.captcha.create()

        # Extracting the generated text
        text = caphash.text

        # Verifying the generated CAPTCHA text with the known CAPTCHA UUID
        self.assertTrue(self.captcha.verify(text, caphash.uuid))
        self.assertFalse(
            self.captcha.verify(text, caphash.uuid)
        )  # Should be False since it's already verified

    def test_verify_invalid(self):
        capdata = self.captcha.create()
        c_text = "WRONGTEXT"
        c_hash = capdata.uuid
        self.assertFalse(self.captcha.verify(c_text, c_hash))

    def test_captcha_html(self):
        caphash = self.captcha.create()
        c_key = gen_captcha_key(
            caphash.unique_salt,
            caphash.text,
            self.captcha.config['SECRET_CAPTCHA_KEY'],
            self.captcha.config['METHOD'],
        )
        html = self.captcha.captcha_html(caphash)
        # Check if the returned value is a string containing HTML
        self.assertIsInstance(html, str)
        self.assertIn('<img', html)
        self.assertIn(
            '<input type="hidden" name="captcha-hash" value="%s">'
            % caphash.uuid,
            html,
        )

    def test_cleanup_old_hashes(self):
        old_caphash = CaptchaHash(
            b64img="b64img",
            text="TEXTTEXT",
            unique_salt="some_unique_salt",  # Replace with the actual value you intend to use
            expires_minutes=-(DEFAULT_CONFIG['EXPIRE_MINUTES'] + 100),
            secret_key=DEFAULT_CONFIG['SECRET_CAPTCHA_KEY'],
            c_hash="some_hash",  # Replace with the actual value you intend to use
        )
        old_caphash.expires = datetime.now() - timedelta(
            minutes=DEFAULT_CONFIG['EXPIRE_MINUTES'] + 100
        )
        self.captcha.captchas[old_caphash.uuid] = old_caphash
        self.captcha.cleanup_old_hashes()
        self.assertNotIn(old_caphash.uuid, self.captcha.captchas)

    def test_captcha_html(self):
        caphash = self.captcha.create()
        html = self.captcha.captcha_html(caphash)
        self.assertIsInstance(html, str)
        self.assertIn('<img', html)
        self.assertIn(
            f'<input type="hidden" name="captcha-hash" value="{caphash.uuid}">',
            html,
        )

    def test_double_verification(self):
        caphash = self.captcha.create()
        text = caphash.text
        self.assertTrue(self.captcha.verify(text, caphash.uuid))
        self.assertFalse(
            self.captcha.verify(text, caphash.uuid)
        )  # Second verification should fail

    # unncecessary but useful for determining impact of
    # captcha generation spam
    def test_brute_gen_captchas(self):
        start = datetime.now()
        caps = set()
        for i in range(100):
            caps.add(self.captcha.create())
            if i % 10 == 0:
                print(i, caps, datetime.now() - start)


if __name__ == '__main__':
    unittest.main()
