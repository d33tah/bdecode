from setuptools import setup, find_packages

setup(
    name='bdecode',
    packages=['bdecode'],
    version='0.1',
    description='A library for decoding of bencoded files',
    license='WTFPL',
    author='Jacek "d33tah" Wielemborek',
    author_email='d33tah+pypi@gmail.com',
    download_url = 'https://github.com/d33tah/bdecode/archive/0.1.tar.gz',
    url='http://github.com/d33tah/bdecode',
    long_description="README.txt",
    scripts = ['bdecode.py'],
    keywords = ['bencoding', 'bittorrent', 'torrent', 'bencode'],
)
