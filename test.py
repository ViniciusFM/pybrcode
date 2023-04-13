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
# output image at ./testingqrcode.svg
pix.imageToPath('.', filename='testingqrcode')
# output image at ./testingqrcode.png
print(pix.toBase64())
print('-------------------------------------')
# output the base64-str version of png qrcode image
print(pix.toSVG())
print('-------------------------------------')
# output the xml-str version of svg qrcode image
print(pix)
# output the pix code used to produce the qrcode
