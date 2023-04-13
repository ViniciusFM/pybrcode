import base64
import io, os
import qrcode
import xml.etree.ElementTree as ET
from pybrcode.exceptions import QRCodeInvalidFilepath

def __gen_svg_qrcode(qr:'qrobj') -> str:
    dqr = qr.get_matrix()
    svg = ET.Element('svg', 
            {'version': '1.1', 'xmlns': 'http://www.w3.org/2000/svg'}
    )
    for r, row in enumerate(dqr):
        for c, val in enumerate(row):
            if val:
                x, y = c * 10, r * 10
                rect = ET.SubElement(svg, 'rect', 
                        {'x': str(x), 'y': str(y), 
                        'width': '10', 'height': '10'}
                )
    width = height = len(dqr) * 10
    svg.set('width', str(width))
    svg.set('height', str(height))
    return ET.tostring(svg, encoding='unicode')

def __gen_bitmap_qrcode(qr:'qrobj') -> 'base64':
    prefix = 'data:image/png;base64,'
    img = qr.make_image(fill_color="black", back_color="white")        
    buff = io.BytesIO()
    img.save(buff)
    buff.seek(0)
    imgb64 = base64.b64encode(buff.read()).decode('utf-8')
    return f'{prefix}{imgb64}'

def generate_qrcode(data:str, svg:bool=True, 
                    dest_dir:str='.', filename:str=None) -> 'str':
    qr = qrcode.QRCode(version=None, 
            error_correction=qrcode.constants.ERROR_CORRECT_L, 
            box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    ret = __gen_svg_qrcode(qr) if svg \
          else __gen_bitmap_qrcode(qr)
    try:
        if filename:
            if svg:
                path = os.path.join(dest_dir, f"{filename}{'.svg'}")
                with open(path, 'w') as f:
                    f.write(ret)
            else:
                path = os.path.join(dest_dir, f"{filename}{'.png'}")
                b64 = base64.b64decode(ret.split(',')[1])
                with open(path, 'wb') as f:
                    f.write(b64)           
    except (IOError, OSError) as e:
        raise QRCodeInvalidFilepath(extra=str(e))
    return ret
