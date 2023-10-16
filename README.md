# flask-simple-captcha

### CURRENT VERSION: **v5.0.0**

**v5.0.0 added an encryption mechanism to the stored text in the jwts. Previous versions are insecure!**


`flask-simple-captcha` is a robust CAPTCHA generator class for generating and validating CAPTCHAs. It allows for easy integration into Flask applications.

See the encryption / decryption breakdown below for more information on the verification mechanism.

## Features

- Generates CAPTCHAs with customizable length and characters
- Easy integration with Flask applications
- Built-in image rendering and line drawing for added complexity
- Base64 image encoding for easy embedding into HTML
- Uses JWTs and Werkzeug password hashing for secure CAPTCHA verification
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

## Encryption and Decryption Breakdown

Uses a combination of JWTs and Werkzeug's password hashing to encrypt and decrypt CAPTCHA text.

### Encryption

1. **Salting the Text**: The CAPTCHA text is salted by appending the secret key at the beginning.
    ```python
    salted_text = secret_key + text
    ```
2. **Hashing**: Werkzeug's `generate_password_hash` function is then used to hash the salted CAPTCHA text.
    ```python
    hashed_text = generate_password_hash(salted_text)
    ```
3. **Creating JWT Token**: A JWT token is generated using the hashed CAPTCHA text and an optional expiration time.
    ```python
    payload = {
        'hashed_text': hashed_text,
        'exp': datetime.utcnow() + timedelta(seconds=expire_seconds),
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')
    ```

### Decryption

1. **Decode JWT Token**: The JWT token is decoded using the secret key. If the token is invalid or expired, the decryption process will fail.
    ```python
    decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
    ```
2. **Extract Hashed Text**: The hashed CAPTCHA text is extracted from the decoded JWT payload.
    ```python
    hashed_text = decoded['hashed_text']
    ```
3. **Verifying the Hash**: Werkzeug's `check_password_hash` function is used to verify that the hashed CAPTCHA text matches the original salted CAPTCHA text.
    ```python
    salted_original_text = secret_key + original_text
    if check_password_hash(hashed_text, salted_original_text):
        return original_text
    ```


## Contributing

Feel free to open a PR. The project has undergone a recent overhaul to improve the code quality.

## License

MIT

Contact: ccarterdev@gmail.com
