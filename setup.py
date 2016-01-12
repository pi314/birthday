import birthday

from setuptools import find_packages, setup


setup(
    name='birthday',
    version=birthday.__version__,
    description='Manage birthdays of your friends.',
    url='https://github.com/pi314/birthday',
    author='Cychih',
    author_email='michael66230@gmail.com',
    maintainer='Cychih',
    maintainer_email='michael66230@gmail.com',
    license='WTFPL',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Rejected :: Do What the Fuck You Want to Public License 2 (WTFPL 2)'
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    packages=find_packages(exclude=['scripts']),
    scripts=['scripts/birthday'],
)
