import sys
import os.path as op
from flask import Flask, request, render_template_string

from flask_simple_captcha import CAPTCHA, DEFAULT_CONFIG

app = Flask(__name__)
test_config = DEFAULT_CONFIG.copy()

CAPTCHA = CAPTCHA(config=test_config)
app = CAPTCHA.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def submit_captcha():
    if request.method == 'GET':
        captcha_dict = CAPTCHA.create()
        capinput = CAPTCHA.captcha_html(captcha_dict)
        return render_template_string(
            '<form method="POST">%s<input type="submit"></form>' % capinput
        )
    if request.method == 'POST':
        c_hash = request.form.get('captcha-hash')
        c_text = request.form.get('captcha-text')

        if CAPTCHA.verify(c_text, c_hash):
            return 'success'
        else:
            return 'failed captcha'


@app.route('/images')
def bulk_captchas():
    num = 50
    captchas = [CAPTCHA.create() for _ in range(num)]
    mimetype = 'image/png' if CAPTCHA.img_format == 'PNG' else 'image/jpeg'
    captchas = [
        '<img class="simple-captcha-img" '
        + 'src="data:%s;base64, %s" />' % (mimetype, c['img'])
        for c in captchas
    ]

    style = '<style>img display: inline-block; margin: 8px;</style>'
    return style + '\n'.join(captchas)


if __name__ == '__main__':
    app.run()
