CAPTCHA_LENGTH = 3

def gen_captcha():
    import random
    import string
    return ''.join(random.sample(string.ascii_lowercase + string.digits, CAPTCHA_LENGTH))


def captcha():
    while True:
        captcha = gen_captcha()
        print('Input captcha to confirm, or Ctrl-C to cancel [{}]'.format(captcha), end=': ')
        if input().strip() == captcha:
            return

        print('Captcha incorrect.')
        print()

color_code = {
    'black': '\033[1;30m',
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[1;34m',
    'magenta': '\033[1;35m',
    'cyan': '\033[1;36m',
    'white': '\033[1;37m',
}

color_code['lime'] = color_code['green']
color_code['purple'] = color_code['magenta']
