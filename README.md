# flask-simple-captcha

### CURRENT VERSION: **v3.0.0**

`flask-simple-captcha` is a robust CAPTCHA generator class that allows for the creation and verification of CAPTCHAs. This class allows for easy integration into various Flask applications.

## Features

- Generates CAPTCHAs with customizable length and characters
- Easy integration with various Flask applications
- Built-in image rendering and line drawing for added complexity
- Base64 image encoding for easy embedding
- JWT-based verification for secure CAPTCHA checks
- Does not require server-side sessions
- Backwards compatible with 1.0 versions of this package

## Prerequisites

- Python 3.7 or higher
- Pillow library for image manipulation

## Installation

You can use this package by directly importing it into your Flask project. Ensure that all dependencies are installed in your environment.

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
        captcha = CAPTCHA.create()
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

## Contributing

Just open a PR. This project was abandoned for years, but as of these most recent commits, has actual quality code but I sunk a weekend into it.

## License

MIT

ccarterdev@gmail.com contact me if you think you will pay me more than i'm being paid currently
