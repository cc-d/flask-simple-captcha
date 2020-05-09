#!/usr/bin/env python3
from flask_simple_captcha.config import config
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import string
import random
import os


class CAPTCHA:
    def __init__(self, default_config=config, config=config):
        self.config = default_config
        for key in config.keys():
            self.config[key] = config[key]

    def random_string(self, min=40, max=50):
        chars = string.ascii_uppercase
        chars = chars + string.ascii_lowercase
        chars = chars + string.digits
    
        ran_int = random.randint(min, max)
        return [random.choice(chars) for i in range(ran_int)]
    
    
    def get_background(self, text_size):
        background = Image.new('RGBA',
                               (int(text_size[0] * 1.25),
                                int(text_size[1] * 1.5)),
                               color=(0, 0, 0, 255))
        return background
    
    
    def draw_lines(self, im, lines=25):
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
                    width=2)
        return im
    
    
    def create(self, length=None, digits=None):
        length = self.config['CAPTCHA_LENGTH'] if length is None else length
        digits = self.config['CAPTCHA_DIGITS'] if digits is None else digits
        size = 30
        width, height = length * size, size
    
        characters = string.digits if digits else string.ascii_uppercase
        text = ''.join([random.choice(characters) for i in range(length)])
    
        base = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    
        txt = Image.new('RGBA', base.size, color=(0, 0, 0, 255))
    
        f_path = os.path.dirname(os.path.realpath(__file__))
        f_path = os.path.join(f_path, 'arial.ttf')
        fnt = ImageFont.truetype(f_path, size)
    
        d = ImageDraw.Draw(txt)
    
        d.text((0, 0), text, font=fnt, fill=(255, 255, 255, 255))
    
        text_img = Image.alpha_composite(base, txt)
    
        text_size = fnt.getsize(text)
        text_size = (int(text_size[0] * 1), int(text_size[1] * 1))
    
        background = self.get_background(text_size)
    
        background.paste(text_img,
                         box=(random.randint(0, background.size[0] - text_size[0]),
                              random.randint(0, background.size[1] - text_size[1])
                              )
                         )
    
        out = background.resize((200, 60))
        out = self.draw_lines(out)
        #out.save('a.png')
    
        c_key = text + self.config['SECRET_CAPTCHA_KEY']
    
        c_hash = generate_password_hash(c_key,
                                        method=self.config['METHOD'],
                                        salt_length=8)
        c_hash = c_hash.replace(self.config['METHOD'] + '$', '')
    
        return {'img': self.convert_b64img(out), 'text': text, 'hash': c_hash}
    
    
    def convert_b64img(self, out):
        byte_array = BytesIO()
        out.save(byte_array, format='PNG')
        byte_array = byte_array.getvalue()
    
        b64image = base64.b64encode(byte_array)
        b64image = str(b64image)
        b64image = b64image[2:][:-1]
    
        return b64image
    
    
    def captcha_html(self, captcha):
        img = '<img class="simple-captcha-img" ' + \
              'src="data:image/png;base64, %s" />' % captcha['img']
    
        inpu = '<input type="text" class="simple-captcha-text"' + \
               'name="captcha-text">\n' + \
               '<input type="hidden" name="captcha-hash" ' + \
               'value="%s">' % captcha['hash']
    
        return '%s\n%s' % (img, inpu)
    
    
    def verify(self, c_text, c_hash, c_key=None):
        c_key = self.config['SECRET_CAPTCHA_KEY'] if c_key is None else c_key
        c_text = c_text.upper()
        c_hash = self.config['METHOD'] + '$' + c_hash
        c_key = c_text + c_key
        return check_password_hash(c_hash, c_key)
    
    
    def init_app(self, app):
        app.jinja_env.globals.update(captcha_html=self.captcha_html)
    
        return app


if __name__ == '__main__':
    print(CAPTCHA().create())
