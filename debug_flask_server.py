from flask import Flask, request, render_template_string
from flask_simple_captcha import CAPTCHA, DEFAULT_CONFIG

app = Flask(__name__)
test_config = DEFAULT_CONFIG.copy()


print(test_config)
CAPTCHA = CAPTCHA(config=test_config)
app = CAPTCHA.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def example():
    if request.method == 'GET':
        captcha = CAPTCHA.create()
        return render_template_string(
            '<form method="post">'
            + '{{ captcha_html(captcha) | safe }}'
            + '<input type="submit"></form>',
            captcha=captcha,
        )
    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')

        if CAPTCHA.verify(c_text, c_hash):
            return 'success'
        else:
            return 'failed captcha'


if __name__ == '__main__':
    app.run()
