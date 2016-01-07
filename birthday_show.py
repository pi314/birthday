from model import Birthday

def birthday_show(args):
    constrains = args.constrains
    for r in Birthday.all():
        print(r)

    print(constrains)
