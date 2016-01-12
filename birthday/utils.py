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
