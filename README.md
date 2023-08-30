### Updated README.md

```markdown
# flask-simple-captcha

### CURRENT VERSION: **v4.1.0**

`flask-simple-captcha` is a robust CAPTCHA generator class for generating and validating CAPTCHAs. It allows for easy integration into Flask applications.

## Features

- Generates CAPTCHAs with customizable length and characters
- Easy integration with Flask applications
- Built-in image rendering and line drawing for added complexity
- Base64 image encoding for easy embedding into HTML
- JWT-based verification for secure CAPTCHA checks
- Successfully submitted CAPTCHAs are stored in-memory to prevent resubmission
- Backwards compatible with 1.0 versions of this package

## Prerequisites

- Python 3.7 or higher
- Pillow library for image manipulation

## Installation

Import this package directly into your Flask project and make sure to install all dependencies.

## How to Use

### Configuration

The CAPTCHA class can be configured with the following options:

```python

DEFAULT_CONFIG = {
    'SECRET_CAPTCHA_KEY': 'CHANGEME - 40 or 50 character long key here',
    'METHOD': 'pbkdf2:sha256:100',
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': False,
    # 'EXPIRE_MINUTES': 10,
    'UNIQUE_SALT_LENGTH': 16,
    # 10 minutes, EXPIRE_SECONDS will take prioritity over EXPIRE_MINUTES
    # if both are set.
    'EXPIRE_SECONDS': 60 * 10,
}
```

Then later:

```python
# normalize jwt expiration time to seconds
if 'EXPIRE_NORMALIZED' not in DEFAULT_CONFIG:
    if 'EXPIRE_MINUTES' in DEFAULT_CONFIG and 'EXPIRE_SECONDS' not in DEFAULT_CONFIG:
        EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_MINUTES'] * 60
    else:
        EXPIRE_NORMALIZED = DEFAULT_CONFIG['EXPIRE_SECONDS']

    DEFAULT_CONFIG['EXPIRE_NORMALIZED'] = EXPIRE_NORMALIZED
```

### Initialization

Add this code snippet at the top of your application:

```python
from flask_simple_captcha import CAPTCHA
SIMPLE_CAPTCHA = CAPTCHA(config=config.CAPTCHA_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)
```

### Protecting a Route

To add CAPTCHA protection to a route, use the following code:

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

In your HTML template, include the following:

```html
<!-- your_template.html -->
<div class="captcha-container">{{ captcha_html|safe }}</div>
```

## License

MIT

---

## Running Tests

1. Install the development requirements:

```bash
pip install -r requirements_dev.txt
```

2. Run the tests:

```bash
python3 tests.py
```

If one wishes to test using a submitted captcha, run the following command:

```bash
python3 debug_flask_server
```



## Contributing

Feel free to open a PR. The project has undergone a recent overhaul to improve the code quality.

## License

MIT

ccarterdev@gmail.com
```

I've updated the README.md to reflect your new code. I removed any mention of server-side sessions and stated that successfully submitted CAPTCHAs are stored in-memory to prevent resubmission. I've also updated the 'How to Use' section to match your updated CAPTCHA class usage.