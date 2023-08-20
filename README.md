# Flask Simple CAPTCHA

A simple CAPTCHA solution for Flask applications. Generate and validate CAPTCHAs to protect your forms from bots. Does not require server side sessions.

## Features

- Customizable CAPTCHA length and characters
- Easy to integrate into Flask applications
- Built-in image rendering
- Utilizes UUID for verification (Note: The hash was previously used for submissions, but now the UUID is used instead.)

## Installation

You can install the package using pip:

```bash
pip3 install flask-simple-captcha
```

Or, if installing from source:

```bash
python3 setup.py install
```

## Configuration

Configure CAPTCHA by passing a dictionary of configuration options to the `CAPTCHA` class. First, you'll want to set a variable `CAPTCHA_CONFIG['SECRET_CAPTCHA_KEY']` in your app config to a random, complex string.

Example:

```python
CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY':'wMmeltW4mhwidorQRli6Oijuhygtfgybunxx9VPXldz'}
```

Here's a table of available options:

| Option                | Description                                                   | Default Value                  |
|-----------------------|---------------------------------------------------------------|--------------------------------|
| `SECRET_CAPTCHA_KEY`  | A secret key for hashing CAPTCHA (40 or 50 characters long)   | 'CHANGEME - 40 or 50 character long key here' |
| `METHOD`              | Hashing method                                                | 'pbkdf2:sha256:100'             |
| `CAPTCHA_LENGTH`      | Length of the CAPTCHA text                                    | 6                              |
| `CAPTCHA_DIGITS`      | Include digits in CAPTCHA text (True/False)                   | False                          |

## How to Use

### Initialization

Add this to the top of your code:

```python
from flask_simple_captcha import CAPTCHA
SIMPLE_CAPTCHA = CAPTCHA(config=config.CAPTCHA_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)
```

### Protecting a Route

For each route you want captcha protected, add the following code:

```python
@app.route('/example', methods=['GET','POST'])
def example():
    if request.method == 'GET':
        captcha = SIMPLE_CAPTCHA.create()
        render_template('example.html', captcha=captcha)
    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if SIMPLE_CAPTCHA.verify(c_text, c_hash):
            return 'success'
        else:
            return 'failed captcha'
```

In the HTML forms, use:

```
{{ captcha_html(captcha) | safe }}
````

 This will create input fields for CAPTCHA.

## Running Tests

1. Install the development requirements:

```bash
pip install -r requirements_dev.txt
```

2. Run the tests:

```bash
python3 tests.py
```

## License

This project is licensed under the MIT License.
