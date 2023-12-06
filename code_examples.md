# Code Examples for Flask-Simple-Captcha

This document provides practical code examples for integrating `flask-simple-captcha` into Flask applications.

## Integration with WTForms and Flask-Security

This example, contributed by Dr. Tobias T. Kranz, demonstrates integrating `flask-simple-captcha` with WTForms and Flask-Security in a Flask application.

### Code for Simple Captcha Field and Validation

```python
import flask
from flask import current_app, request
from markupsafe import Markup
from wtforms import Field, ValidationError

SIMPLE_CAPTCHA_ERROR_CODES = {
    "missing-input-hash": "The secret parameter is missing.",
    "missing-input-response": "The response parameter is missing.",
    "invalid-captcha-sol": "The captcha was not entered correctly.",
}

class SimpleCaptchaWidget:
    def simplecaptcha_html(self):
        simple_captcha = flask.current_app.extensions.get("flask-simple-captcha")
        captcha_dict = simple_captcha.create()
        return Markup(simple_captcha.captcha_html(captcha_dict))

    def __call__(self, field, error=None, **kwargs):
        return self.simplecaptcha_html()

class SimpleCaptcha:
    def __init__(self, message=None):
        self.message = message
        self._simple_captcha = current_app.extensions.get("flask-simple-captcha")

    def __call__(self, form, field):
        if current_app.testing:
            return True

        if request.is_json:
            c_hash = request.json.get('captcha-hash')
            c_text = request.json.get('captcha-text')
        else:
            c_hash = request.form.get('captcha-hash')
            c_text = request.form.get('captcha-text')

        if not c_hash:
            self.message = SIMPLE_CAPTCHA_ERROR_CODES["missing-input-hash"]
            raise ValidationError(field.gettext(self.message))
        if not c_text:
            self.message = SIMPLE_CAPTCHA_ERROR_CODES["missing-input-response"]
            raise ValidationError(field.gettext(self.message))

        if not self._validate_simple_captcha(c_hash, c_text):
            self.message = SIMPLE_CAPTCHA_ERROR_CODES["invalid-captcha-sol"]
            raise ValidationError(field.gettext(self.message))

    def _validate_simple_captcha(self, c_hash, c_text):
        if self._simple_captcha.verify(c_text, c_hash):
            return True
        return False

class SimpleCaptchaField(Field):
    widget = SimpleCaptchaWidget()

    def __init__(self, label="", validators=None, **kwargs):
        validators = validators or [SimpleCaptcha()]
        super().__init__(label, validators, **kwargs)
```

### Implementing in a Custom Form

Use the `SimpleCaptchaField` in your custom forms as follows:

```python
from flask_security.forms import RegisterForm
from wtforms import StringField, DataRequired

class CustomRegisterForm(RegisterForm):
    captcha = SimpleCaptchaField("Captcha")
    first_name = StringField("First name", [DataRequired()])
```

### HTML Form Integration

Include the CAPTCHA field in your HTML templates:

```html
<form
  action="{{ url_for_security('register') }}"
  method="post"
  name="register_user_form"
  id="register_user_form"
>
  <!-- ... other form elements ... -->
  {{ render_field_with_errors(your_form.captcha, class_="form-control")}}
</form>
```
