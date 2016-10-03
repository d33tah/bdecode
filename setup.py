from setuptools import setup, find_packages

setup(
    name='bdecode',
    version='0.1',
    license='WTFPL',
    author='Jacek "d33tah" Wielemborek',
    author_email='d33tah+pypi@gmail.com',
    url='http://github.com/d33tah/bdecode',
    long_description="README.txt",
    packages=find_packages(),
    scripts = ['bdecode.py'],
    description='A library for decoding of bencoded files',
)
