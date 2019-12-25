from PIL import Image, ImageDraw, ImageFont

def create_captcha(length):
    img = Image.new('RGB', (50, 50), color='white')
    d = ImageDraw.Draw(img)

    d.text((10,10), 'hhhhhhhhh', fill=(255,255,255,128))
    img.save('a.png')

def main():
    create_captcha(0)

if __name__ == '__main__':
    main()