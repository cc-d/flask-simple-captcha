# flask-simple-captcha

### CURRENT VERSION: **v4.2.1**

`flask-simple-captcha` is a robust CAPTCHA generator class for generating and validating CAPTCHAs. It allows for easy integration into Flask applications.

## Features

- Generates CAPTCHAs with customizable length and characters
- Easy integration with Flask applications
- Built-in image rendering and line drawing for added complexity
- Base64 image encoding for easy embedding into HTML
- JWT-based verification for secure CAPTCHA checks
- Successfully submitted CAPTCHAs are stored in-memory to prevent resubmission
- Backwards compatible with 1.0 versions of this package
- Avoids visually similar characters by default
- Supports custom character set provided by user
- Casing of submitted captcha is ignored by default

## Prerequisites

- Python 3.7 or higher
- Werkzeug >=0.16.0, <3
- Pillow <=9.0.0
- myfuncs >=1.4.8


## Installation

Import this package directly into your Flask project and make sure to install all dependencies.

## How to Use

### Configuration

```python
DEFAULT_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'LONG SECRET KEY HERE',  # use for JWT encoding/decoding
    'CAPTCHA_LENGTH': 6,  # Length of the generated CAPTCHA text
    'CAPTCHA_DIGITS': False,  # Should digits be added to the character pool?
    # EXPIRE_SECONDS will take prioritity over EXPIRE_MINUTES if both are set.
    'EXPIRE_SECONDS': 60 * 10,
    #'EXPIRE_MINUTES': 10, # backwards compatibility concerns supports this too
    #'EXCLUDE_VISUALLY_SIMILAR': True,  # Optional
    #'ONLY_UPPERCASE': True,  # Optional
    #'CHARACTER_POOL': 'AaBb',  # Optional
}
```

### Initialization

Add this code snippet at the top of your application:

```python
from flask_simple_captcha import CAPTCHA
SIMPLE_CAPTCHA = CAPTCHA(config=config.CAPTCHA_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)
```

### Protecting a Route

To add CAPTCHA protection to a route, you can use the following code:

```python
@app.route('/example', methods=['GET','POST'])
def example():
    if request.method == 'GET':
        new_captcha_dict = SIMPLE_CAPTCHA.create()
        render_template('example.html', captcha=new_captcha_dict)
    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if SIMPLE_CAPTCHA.verify(c_text, c_hash):
            return 'success'
        else:
            return 'failed captcha'
```

In your HTML template, you need to wrap the CAPTCHA inputs within a form element. The package will only generate the CAPTCHA inputs but not the surrounding form or the submit button.

```html
<!-- your_template.html -->
<form action="/example" method="post">
  {{ captcha_html(captcha)|safe }}
  <input type="submit" value="Submit">
</form>
```

## Debugging

You can run `debug_flask_server.py` for minimal testing on port `5000`. This allows you to test the generated CAPTCHA HTML and submission behavior.

```bash
# Might want to use venv
pip3 install -r requirements_dev.txt

python3 debug_flask_server.py
```

## Running Tests

1. Install the development requirements:

```bash
pip install -r requirements_dev.txt
```

2. Run the tests:

```bash
python3 tests.py
```

or

```bash
python3 -m unittest tests.py
```

## Contributing

Feel free to open a PR. The project has undergone a recent overhaul to improve the code quality.

## License

MIT

Contact: ccarterdev@gmail.com
