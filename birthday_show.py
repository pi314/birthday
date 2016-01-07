from model import Birthday

def birthday_show(args):
    for r in Birthday.all():
        print(r)
