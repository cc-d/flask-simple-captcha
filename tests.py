import unittest
from datetime import datetime, timedelta
from flask_simple_captcha import CaptchaHash, CAPTCHA, DEFAULT_CONFIG
from werkzeug.security import generate_password_hash


class TestCAPTCHA(unittest.TestCase):
    def setUp(self):
        self.captcha = CAPTCHA(DEFAULT_CONFIG)

    def test_create(self):
        caphash = self.captcha.create()

        # Check if the returned value is a CaptchaHash object
        self.assertIsInstance(caphash, CaptchaHash)

        self.assertEqual(len(caphash.text), DEFAULT_CONFIG['CAPTCHA_LENGTH'])

    def test_verify_valid(self):
        text = 'TESTTEXT'
        c_key = (
            text
            + DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
            + self.captcha.unique_salt
        )
        c_hash = generate_password_hash(c_key, method=DEFAULT_CONFIG['METHOD'])

        caphash = CaptchaHash(
            b64img="b64img",
            text="TEXTTEXT",
            unique_salt=self.captcha.unique_salt,
            expires_minutes=1,
            secret_key=c_key,
            c_hash=c_hash,
        )

        self.captcha.captchas[caphash.uuid] = caphash

        self.assertTrue(self.captcha.verify(text, caphash.uuid))
        self.assertFalse(self.captcha.verify(text, caphash.uuid))

    def test_verify_invalid(self):
        capdata = self.captcha.create()
        c_text = "WRONGTEXT"
        c_hash = capdata.uuid
        self.assertFalse(self.captcha.verify(c_text, c_hash))

    def test_cleanup_old_hashes(self):
        # Add an old CAPTCHA entry
        text = 'TESTTEXT'
        c_key = (
            text
            + DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
            + self.captcha.unique_salt
        )
        c_hash = generate_password_hash(c_key, method=DEFAULT_CONFIG['METHOD'])
        caphash = CaptchaHash(
            secret_key=c_key,
            c_hash=c_hash,
            b64img="b64img",
            text="TEXTTEXT",
            unique_salt=self.captcha.unique_salt,
            expires_minutes=-(self.captcha.config['EXPIRE_MINUTES'] + 100),
        )

        c_key = (
            'TESTTEST'
            + DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
            + caphash.unique_salt
        )
        c_hash = generate_password_hash(c_key, method=caphash.method)

        # Manually set created time to past
        caphash.expires = datetime.now() - timedelta(
            minutes=self.captcha.config['EXPIRE_MINUTES'] + 100
        )

        self.captcha.cleanup_old_hashes()

        self.assertTrue(caphash.uuid not in self.captcha.captchas)

    def test_captcha_html(self):
        caphash = self.captcha.create()
        c_key = (
            caphash.text
            + DEFAULT_CONFIG['SECRET_CAPTCHA_KEY']
            + caphash.unique_salt
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


if __name__ == '__main__':
    unittest.main()
