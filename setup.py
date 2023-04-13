from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n\n" + fh.read()

long_description = "\nGo to github [README.md](https://github.com/ViniciusFM/pybrcode/blob/main/README.md) to see this text in good format. Link: https://github.com/ViniciusFM/pybrcode/blob/main/README.md"+long_description

VERSION = '1.1'
DESCRIPTION = 'Generate Pix QRCodes with any type of key'
LONG_DESCRIPTION = 'The pybrcode is a python3 library that was built to help people to generate Pix QRCodes (BRCodes) using easy-to-understand and well documented functions.'

# Setting up
setup(
    name="pybrcode",
    version=VERSION,
    author="viniciusmacielf (Vinícius Fonseca Maciel)",
    author_email="<viniciusmacielf@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['crcmod', 'qrcode', 'Unidecode'],
    keywords=['python', 'pix', 'qrcode', 'brcode', 'svg pix qrcode'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
)