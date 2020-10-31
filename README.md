# Install
`pip3 install flask-simple-captcha`
or if installing from source
```python3 setup.py install```

# How to use
This package is intended to assign a unique CSRF string per each form submit per user session, without requiring any backend session tracking. First, you'll want to set a variable `CAPTCHA_CONFIG['SECRET_CAPTCHA_KEY']` in your app config to a random, complex string. Example: `CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY':'wMmeltW4mhwidorQRli6Oijuhygtfgybunxx9VPXldz'}`

Second, add this to the top of your code.

```
from flask_simple_captcha import CAPTCHA
CAPTCHA = CAPTCHA(config=config.CAPTCHA_CONFIG)
app = CAPTCHA.init_app(app)
```

For each route you want captcha protected, add the following code:

```
@app.route('/example, methods=['GET','POST']
def example():
    if request.method == 'GET':
        captcha = CAPTCHA.create()
        render_template('example.html', captcha=captcha)
    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')
        if CAPTCHA.verify(c_text, c_hash):
            return 'success'
        else:
            return 'failed captcha'
```
        

In the HTML forms you want to generate a captcha: `{{ captcha_html(captcha) }}`

This will create something like this:
```
<input type="text" name="captcha-text">
<input type="hidden" name="captcha-hash" value="1o9ig...">
```
