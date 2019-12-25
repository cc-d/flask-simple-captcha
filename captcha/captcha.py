from PIL import Image, ImageDraw, ImageFont
import string
import random

def get_background(text_size):
    background = Image.new('RGBA', (int(text_size[0] * 1.25), int(text_size[1] * 1.5)), color=(0,0,0,255))
    return background

def draw_lines(im, lines=10):
    draw = ImageDraw.Draw(im)

    for i in range(lines):
        print(im.size)

        if random.randint(0,1) == 0:
            draw.line((
                        random.randint(0, im.size[0]),
                        0,
                        random.randint(0, im.size[0]),
                        im.size[1],
                    ), width=2)
        else:
            draw.ellipse((
                        random.randint(-80, im.size[0]),
                        random.randint(-80, -10),
                        random.randint(-80, im.size[0]),
                        im.size[1] + random.randint(10, 80),
                    ), width=4)
    return im


def create_captcha(length=5, digits=False):
    size = 30
    width, height = length * size, size

    characters = string.digits if digits else string.ascii_uppercase
    text = ''.join([random.choice(characters) for i in range(length)])

    base = Image.new('RGBA', (width, height), color=(0,0,0,0))

    txt = Image.new('RGBA', base.size, color=(0,0,0,255))

    fnt = ImageFont.truetype('arial.ttf', size)

    d = ImageDraw.Draw(txt)

    d.text((0, 0), text, font=fnt, fill=(255,255,255,255))
    
    text_img = Image.alpha_composite(base, txt)

    text_size = fnt.getsize(text)
    text_size = (int(text_size[0] * 1), int(text_size[1] * 1))

    background = get_background(text_size)

    background.paste(text_img,
                    box=(
                        random.randint(0,background.size[0] - text_size[0]),
                        random.randint(0, background.size[1] - text_size[1])
                        )
                    )

    out = background.resize((200, 60))
    out = draw_lines(out)
    out.save('a.png')

def main():
    create_captcha(5, True)

if __name__ == '__main__':
    main()