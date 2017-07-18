from distutils.core import setup
setup(
    name = 'businessru-api',
    packages = ['businessru_api'],
    version = '0.1',
    description = 'small wrapper around business.ru API',
    author = 'Oleg Shigorin',
    author_email = 'mail@olegshigor.in',
    url = 'https://github.com/nuqlear/businessru-api',
    download_url = 'https://github.com/nuqlear/businessru-api/archive/0.1.tar.gz',
    keywords = ['business.ru', 'businessru'],
    install_requires=[
        'requests==2.18.1'
    ],
)