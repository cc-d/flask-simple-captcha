# Code Examples for Flask-Simple-Captcha

This document provides practical code examples for integrating `flask-simple-captcha` into Flask applications.

## Integration with WTForms and Flask-Security

This example, contributed by [@TobiasTKranz](https://www.github.com/TobiasTKranz), demonstrates integrating `flask-simple-captcha` with WTForms and Flask-Security in a Flask application.

### Code to access Simple Captcha easily inside your project

In order to access the Simple Captcha Extension you might connect it to the flask extensions dict like that:

```python
# Fake extension registration, to be able to access this extension's instance later on
app.extensions.update({"flask-simple-captcha": SIMPLE_CAPTCHA})
```

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
    def __call__(self, field, error=None, **kwargs):
        simple_captcha = flask.current_app.extensions.get("flask-simple-captcha")
        captcha_dict = simple_captcha.create()

        return Markup(simple_captcha.captcha_html(captcha_dict))

class SimpleCaptcha:
    def __init__(self):
        self._simple_captcha = current_app.extensions.get("flask-simple-captcha")

    def __call__(self, form, field):
        if current_app.testing:
            return True

        request_data = request.json if request.is_json else request.form
        c_hash = request_data.get('captcha-hash')
        c_text = request_data.get('captcha-text')

        if not c_hash:
            raise ValidationError(
                SIMPLE_CAPTCHA_ERROR_CODES["missing-input-hash"]
            )
        elif not c_text:
            raise ValidationError(
                SIMPLE_CAPTCHA_ERROR_CODES["missing-input-response"]
            )
        elif not self._validate_simple_captcha(c_hash, c_text):
            raise ValidationError(
                SIMPLE_CAPTCHA_ERROR_CODES["invalid-captcha-sol"]
            )

    def _validate_simple_captcha(self, c_hash, c_text):
        return self._simple_captcha.verify(c_text, c_hash)

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
