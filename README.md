What is this library for?
=========================

The **pybrcode** is a python3 library that was built to help people to generate Pix QRCodes (BRCodes) using easy-to-understand and well documented functions. In most scenarios you will only need one function to generate a Pix: `generate_simple_pix(...)`

Go to [How to use?](#how-to-use) section to learn how to use this function.

You can customize the Pix payload
---------------------------------

Although it is easy-to-use, you can customize the Pix payload following the BRCode specification by Central Bank of Brazil (BCB). You can do this by trying to instantiate the `Pix` object by yourself and following the BCB's manuals: [pt-BR](https://www.bcb.gov.br/content/estabilidadefinanceira/SiteAssets/Manual%20do%20BR%20Code.pdf) and [en-US](https://www.bcb.gov.br/content/config/Documents/BR_Code_MANUAL_Version_2_May_2020.pdf)

The custom Pix payload will be generated by fulfilling the "Payload Dictionary" with `Data` tree objects, which can be seen at [pybrcode.pix.Data](pybrcode/pix.py) class. The payload is as follows:

PS: the `crc16` payload field is autogenerated at string conversion of the Pix object (i.e. `str(pix)`). The used CRC algorithm is **CRC-16-CCITT-FFFF** (also called CRC/16-CCITT-FALSE) as described by the BRCode Manual by BCB:
```
Poly=0x1021, Init=0xFFFF, RefIn=false, RefOut=false, XorOut=0x0000
```

```python
class Data(object):
    '''This is a Data tree containing a TLV 
    (type|id, length, value) in each "node".
    Convert the object to string to get the
    pix payload format'''
    def __init__(self, id:int, value:'str|list(Data)'):
        self.id = id
        self.__length = None
        self.value = value

#(code...)

class Pix(object):
    '''
        Creates a Pix Object  that  supports image conversion
        to "BRCode" format (Pix QRCode). The payload is based 
        at EMV QRCode model,  some  of the fields are already 
        fulfilled according to Pix specifications.
        Each field of the payload  dict must receive a 'Data'
        object, which is a TLV  type  object. The  "optional"
        fields are "nullable" fields.
        The payload dict contains these informations:
            pfi     -> Payload Format Indicator (def. 01),
            poim    -> Point of Initiation Method 
                       (def. 12 - optional),
            mai     -> Merchant Account Information,
            mcc     -> Merchant Category Code (def. 0000),
            tcurr   -> Transaction Currency (def. 986),
            tamount -> Transaction Amount (optional),
            ccode   -> Country Code (def. 58),
            mname   -> Merchant Name,
            mcity   -> Merchant City,
            pcode   -> Postal Code (optional),
            adft    -> Aditional Data Field Template,
            ut      -> Unreserved Templates (optional),
            crc16   -> Cyclic Redundancy Check 16 bits
        Convert the object to string  to get the pix  payload
        format.
        The  'crc16'  field  is  automatically  generated  at
        conversion of the Pix object to string __str__.
    '''
    def __init__(self):
        self.payload: dict = {
            'pfi'       : Data(0, '01'),
            'poim'      : Data(1, '12'),
            'mai'       : None,
            'mcc'       : Data(52, '0000'),
            'tcurr'     : Data(53, '986'),
            'tamount'   : None,
            'ccode'     : Data(58, 'BR'),
            'mname'     : None,
            'mcity'     : None,
            'pcode'     : None,
            'adft'      : None,
            'ut'        : None,
            'crc16'     : None
        }

#(code...)
```

Installation
============

Easy way (PyPi repositories)
----------------------------
By writing this line at your favorite terminal you can download the `pybrcode` library to use for your project.
```properties
pip3 install pybrcode
```

Other way (downloading this code)
--------------------------------
You can hit download button or clone this repository to your own project src directory.

Before using this library as a dependency you'll need to download the required libraries to use it. You can do this by writing the line below at your favorite terminal:

```properties
pip3 install -r requirements.txt
```

How to use?
===========

To create your own Pix QRCode all you need, in most cases, is to call the `generate_simple_pix` function. Then you can choose how to export the generated code by calling the following methods of Pix object:
```python
Pix.toBase64(self) # returns a bitmap in a Base64 string.
Pix.toSVG(self) # returns a vector in a SVG string.
Pix.imageToPath(self, destDir:str, filename:str="image", svg:str=False)
# saves a bitmap (PNG) or vector (SVG) in a file at 'destDir'.
Pix.__str__(self) # generate the entire pix payload as string.
```

The `generate_simple_pix` prototype can be seen below:

```python
def generate_simple_pix(
        fullname:str, key:str, 
        city:str, value:float, pix_id:str=None,
        pcode:str=None, description:str=None,
        mult_transaction:bool=False) -> 'Pix':
    '''
    raise PixInvalidPayloadException
    raise PixInvalidKeyException
    This creates a simple functional Pix object.
    These are the formats acceptable for keys:
        CPF     -> ###.###.###-##
        CNPJ    -> ##.###.###/####-##
        Phone   -> (##) ####-#### / (##) #####-####
        Email   -> ###@###.###
        RandKey -> len(key) == 36
    Information about fields:
        * strings will be transformed to lose
          accentuation.
        fullname -> length [1..25],
        key      -> will be tested
        city     -> length [1..15],
        value    -> rounded to 2 decimals
        pix_id   -> length [1..25],
            * if pix_id omitted, a random
              25ch string will be generated.
        pcode    -> length [1..99] (no treatment)
            * pcode is optional
        description -> length[1..N]
            * N = 73-len(key)
            * description is optional
            * if len(description) not in [1..N]
              description will be discarted.
    Returns:
        Pix Object
    '''

#(code)
```
A simple example using **pybrcode**
-----------------------------------

This example uses all methods and functions mentioned before. You can find this code at [test.py](test.py).

```python
from pybrcode.pix import generate_simple_pix

# This will create a R$ 3,00 pix addressed to:
# 406c5d72-e8e1-40dd-87a9-f7846d08f9e1.
# This pix can accept more than one 
# payment (mult_transaction), so you can 
# try reading the QRCode to buy me a R$ 3,00
# shot of cachaça :)
pix = generate_simple_pix(
    fullname="Vinicius Fonseca Maciel",
    key="406c5d72-e8e1-40dd-87a9-f7846d08f9e1",
    city="Patos de Minas", 
    value=3.00,
    mult_transaction=True,
    description="A shot of cachaça!")

pix.imageToPath('.', filename='testingqrcode', svg=True)
# output image created at ./testingqrcode.svg
pix.imageToPath('.', filename='testingqrcode')
# output image created at ./testingqrcode.png
print(pix.toBase64())
print('-------------------------------------')
# output the base64-str version of png qrcode image
print(pix.toSVG())
print('-------------------------------------')
# output the xml-str version of svg qrcode image
print(pix)
# output the pix code used to produce the qrcode

```

Buy me a shot of cachaça, please?
=================================

If you find this library helpful you're welcome to buy me a shot of cachaça which cost only R$ 3,00 at "Bar do Cabaça"! :D

Just read this BRCode with your bank app:

<img src="./testingqrcode.png" alt="Donate R$ 3,00 by reading this QRCode" width="256">
