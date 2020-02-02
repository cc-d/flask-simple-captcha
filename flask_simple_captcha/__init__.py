#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import string
import random


HTML_ELEM_NAME = 'simplecaptcha'
SECRET_CAPTCHA_KEY = 'CHANGEME - 40 or 50 character long key here'
METHOD = 'pbkdf2:sha256:100'


def random_string(min=40, max=50):
    chars = string.ascii_uppercase
    chars = chars + string.ascii_lowercase
    chars = chars + string.digits

    ran_int = random.randint(min, max)
    return [random.choice(chars) for i in range(ran_int)]


def get_background(text_size):
    background = Image.new('RGBA',
                           (int(text_size[0] * 1.25),
                            int(text_size[1] * 1.5)),
                           color=(0, 0, 0, 255))
    return background


def draw_lines(im, lines=10):
    draw = ImageDraw.Draw(im)

    for i in range(lines):
        if random.randint(0, 1) == 0:
            draw.line(
                     (random.randint(0, im.size[0]),
                      0,
                      random.randint(0, im.size[0]),
                      im.size[1],),
                width=2)
        else:
            draw.ellipse(
                        (random.randint(-80, im.size[0]),
                         random.randint(-80, -10),
                         random.randint(-80, im.size[0]),
                         im.size[1] + random.randint(10, 80),),
                width=4)
    return im


def create(length=5, digits=False):
    size = 30
    width, height = length * size, size

    characters = string.digits if digits else string.ascii_uppercase
    text = ''.join([random.choice(characters) for i in range(length)])

    base = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))

    txt = Image.new('RGBA', base.size, color=(0, 0, 0, 255))

    fnt = ImageFont.truetype('arial.ttf', size)

    d = ImageDraw.Draw(txt)

    d.text((0, 0), text, font=fnt, fill=(255, 255, 255, 255))

    text_img = Image.alpha_composite(base, txt)

    text_size = fnt.getsize(text)
    text_size = (int(text_size[0] * 1), int(text_size[1] * 1))

    background = get_background(text_size)

    background.paste(text_img,
                     box=(random.randint(0, background.size[0] - text_size[0]),
                          random.randint(0, background.size[1] - text_size[1])
                          )
                     )

    out = background.resize((200, 60))
    out = draw_lines(out)
    #out.save('a.png')

    c_key = text + SECRET_CAPTCHA_KEY

    c_hash = generate_password_hash(c_key,
                                    method=METHOD,
                                    salt_length=8)
    c_hash = c_hash.replace(METHOD + '$', '')

    return {'img': convert_b64img(out), 'text': text, 'hash': c_hash}


def convert_b64img(out):
    byte_array = BytesIO()
    out.save(byte_array, format='PNG')
    byte_array = byte_array.getvalue()

    b64image = base64.b64encode(byte_array)
    b64image = str(b64image)
    b64image = b64image[2:][:-1]

    return b64image


def html(captcha):
    img = '<img src="data:image/png;base64, %s />' % captcha['img']

    inpu = '<input type="text" name="captcha-text">\n' + \
           '<input type="hidden" name="captcha-hash" ' + \
           'value="%s">' % captcha['hash']

    return '%s\n%s' % (img, inpu)


def verify(c_text, c_hash, c_key=SECRET_CAPTCHA_KEY):
    c_text = c_text.upper()
    c_hash = METHOD + '$' + c_hash
    c_key = c_text + c_key
    return check_password_hash(c_hash, c_key)


def init_app(app):
    app.jinja_env.globals.update(csrf_html=csrf_html)

    if 'SECRET_CAPTCHA_KEY' in app.config.keys():
        SECRET_CAPTCHA_KEY = app.config['SECRET_CAPTCHA_KEY']
    else:
        print('SECRET_CAPTCHA_KEY does not exist in app config.' +
              'You should not use the default.')

    return app


def main():
    print(create())

if __name__ == '__main__':
    main()