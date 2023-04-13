import crcmod, re, random
import unidecode, string
from pybrcode.qrcode import generate_qrcode
from pybrcode.exceptions import PixInvalidKeyException
from pybrcode.exceptions import PixInvalidPayloadException

crc16 = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, 
                        xorOut=0x0000, rev=False)

def treat_string(str_data):
    data_decoded = unidecode.unidecode(str_data)
    return data_decoded.translate({ord(c):None for c in '\n\t\r'})

class Data(object):
    '''This is a Data tree containing a TLV 
    (type|id, length, value) in each "node".
    Convert the object to string to get the
    pix payload format'''
    def __init__(self, id:int, value:'str|list(Data)'):
        self.id = id
        self.__length = None
        self.value = value
    def __len__(self) -> int:
        '''Not O(1)'''
        if not self.__length:
            if(type(self.value) == str):
                self.__length = len(self.value)
            else:
                self.__length = 0
                for d in self.value:
                    self.__length += 4 + len(d)
        return self.__length
    def __str__(self):
        #int with 2 digits min
        idstr = "{0:0{1}}".format(self.id,2)
        lstr = "{0:0{1}}".format(len(self),2)
        if len(idstr) > 2: 
            raise PixInvalidPayloadException(
                extra=f'Invalid ID {idstr}.')
        if len(lstr) > 2:
            raise PixInvalidPayloadException(
                extra=f'Invalid length {lstr} for ID {idstr}.')
        string = f'{idstr}{lstr}'
        if type(self.value) == str:
            string += self.value
        else:
            for s in self.value:
                string += str(s)
        return string

class Pix(object):
    '''
        Creates a Pix Object  that  supports image conversion
        to "BRCode" format (Pix QRCode). The payload is based 
        at EMV QRCode model,  some  of the fields are already 
        fulfilled accordingly to Pix specifications.
        Each field of the payload  dict must receive a 'Data'
        object, which is a TLV type object. Those  "optional"
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
    def __checkId(self, reqKey:str, reqId:'int|tuple', optional=False):
        try:
            p = self.payload
            if optional and not p[reqKey]:
                p[reqKey] = ''
                return
            if p[reqKey].__class__.__name__ != Data.__name__:
                raise AttributeError()
            if type(reqId) == tuple:
                if not (reqId[0] < p[reqKey].id < reqId[1]):
                    raise PixInvalidPayloadException(
                        extra=f'Wrong id for "{reqKey}": ival {reqId}.')
                return
            elif p[reqKey].id != reqId:
                raise PixInvalidPayloadException(
                    extra=f'Wrong id for "{reqKey}": must be {reqId}.')
        except AttributeError as e:
            raise PixInvalidPayloadException(
                extra=f'Wrong value format for "{reqKey}".')
    def __validates(self):
        self.__checkId('pfi', 0)
        self.__checkId('poim', 1, True)
        self.__checkId('mai', (25, 52))
        self.__checkId('mcc', 52)
        self.__checkId('tcurr', 53)
        self.__checkId('tamount', 54, True)
        self.__checkId('ccode', 58)
        self.__checkId('mname', 59)
        self.__checkId('mcity', 60)
        self.__checkId('pcode', 61, True)
        self.__checkId('adft', 62)
        self.__checkId('ut', (79,100), True)
    def setMultipleTransaction(self, on:bool):
        self.payload['poim'] = Data(1, '11') \
                    if on else Data(1, '12')
    def setMaiKey(self, key:'Data', description:str=None):
        '''set merchant account information as
        default id(26), BR.GOV.BCB.PIX as GUI
        and "key" as pix key. No treatment
        to key value. Use PixKeyUri.toData() 
        to produce key.
        Description max size is defined by:
        99 minus len('0014BR.GOV.BCB.PIX')
        minus len('01XX') minus len(key)
        minus len('02XX').
        Which is:
        99 - 18 - 4 - len(key) - 4.
        If key length is 36, in random key example,
        the description size is: 37 characters max
        For reference:
            if key is CPF     -> 62ch long
            if key is CNPJ    -> 59ch long
            if key is Phone   -> 58ch long
            if key is Email   -> no reference
            if key is RandKey -> 37 ch
        The e-mail is tricky. :')
        ** The description will be descarted if there's no
        room for it. **
        '''
        if description and 0 < len(description) <= 73-len(key.value):
            self.payload['mai'] = Data(26, [
                Data(0, 'BR.GOV.BCB.PIX'),
                key,
                Data(2, description)
            ])
        else:
            self.payload['mai'] = Data(26, [
                Data(0, 'BR.GOV.BCB.PIX'),
                key
            ])
    def setTamount(self, amount:float):
        '''set transaction amount. The
        amount value will be rounded to
        have 2 decimals like the currency
        format.'''
        self.payload['tamount'] = Data(54,
            "{0:.2f}".format(amount))
    def setMname(self, mname:str):
        '''set merchant name, length
        must be at least 1 and max 25'''
        n = treat_string(mname)
        if not 0 < len(n) < 26:
            raise PixInvalidPayloadException(
                extra="mname length must be [1..25]."
            )
        self.payload['mname'] = Data(59, n)
    def setMcity(self, mcity:str):
        '''set merchant city, length
        must be at least 1 and max 15'''
        n = treat_string(mcity)
        if not 0 < len(n) < 16:
            raise PixInvalidPayloadException(
                extra="mcity length must be [1..15]."
            )
        self.payload['mcity'] = Data(60, n)
    def setPixID(self, pixid:str):
        '''set aditional data field template
        with an special id, length must be at 
        least 1 and max 25.'''
        n = treat_string(pixid)
        n.strip().replace(' ', '')
        if not 0 < len(n) < 26:
            raise PixInvalidPayloadException(
                extra="pix id length must be [1..25]."
            )
        self.payload['adft'] = Data(62, [
            Data(5, pixid)
        ])
    def toBase64(self) -> str:
        '''raise PixInvalidPayloadException
        This method generates base64 string
        version of the QRCode'''
        return generate_qrcode(str(self), svg=False)
    def toSVG(self) -> str:
        '''raise PixInvalidPayloadException
        This  method  generates  SVG string
        version of the QRCode'''
        return generate_qrcode(str(self))
    def imageToPath(self, destDir:str, filename:str="image", svg:str=False):
        '''raise PixInvalidPayloadException
        This   method  generates  an  image
        version of the QRCode.
        destDir  -> Destination directory where
                    the image will be saved
        filename -> image file name without
                    extension (def. image)
        svg      -> if the image should be
                    a SVG (True) or PNG (False)
        '''
        generate_qrcode(str(self), svg, destDir, filename)
    def __str__(self) -> str:
        '''raise PixInvalidPayloadException
        Prints the pix payload in string format.'''
        self.__validates()
        p = self.payload
        pstr = f"{p['pfi']}{p['poim']}{p['mai']}" \
               f"{p['mcc']}{p['tcurr']}{p['tamount']}" \
               f"{p['ccode']}{p['mname']}{p['mcity']}" \
               f"{p['pcode']}{p['adft']}{p['ut']}"
        pbytes = bytes(pstr+'6304', 'utf-8')
        result = crc16(pbytes)
        p['crc16'] = Data(63, '{:04X}'.format(result))
        return f"{pstr}{p['crc16']}"

class PixType(object):
    CPF = 'cpf'
    CNPJ = 'cnpj'
    BRPHONE = 'BRphone'
    EMAIL = 'email'
    RANDKEY = 'random key'

class PixKeyURI(object):
    '''
    Creates and test a Pix key accordingly to
    one of these formats: CPF, BRPHONE, EMAIL,
    RANDKEY.
    Acceptable phone numbers are only in BR
    Format.
    Random key is basically anything that 
    has a 36 character long string.
    These are the formats acceptable for keys:
        CPF     -> ###.###.###-##
        CNPJ    -> ##.###.###/####-##
        Phone   -> (##) ####-#### / (##) #####-####
        Email   -> ###@###.###
        RandKey -> len(key) == 36
    '''
    def __init__(self, key:str):
        self.type = None
        if '@' in key:
            self.type = PixType.EMAIL
        elif len(key) < 16 and '(' in key:
            self.type = PixType.BRPHONE
        elif '.' in key and '/' in key:
            self.type = PixType.CNPJ
        elif '.' in key and '-' in key:
            self.type = PixType.CPF
        else:
            self.type = PixType.RANDKEY
        self.key = key.strip().replace(' ', '')
        self.__validates()
    def __testAndFormatKeyCNPJ(self) -> bool:
        self.key = re.sub(r'[\.\/\-]', '', self.key)
        if len(self.key) != 14 or \
            self.key in (c * 14 for c in "123456789"): 
            return False
        v1 = [5,4,3,2,9,8,7,6,5,4,3,2]
        v2 = [6,5,4,3,2,9,8,7,6,5,4,3,2]
        s1 = 11 - sum(int(self.key[i]) * v1[i] for i in range(12)) % 11
        s2 = 11 - sum(int(self.key[i]) * v2[i] for i in range(13)) % 11
        s1 = 0 if s1 > 9 else s1
        s2 = 0 if s2 > 9 else s2
        return s1 == int(self.key[12]) and s2 == int(self.key[13])
    def __testAndFormatKeyCPF(self) -> bool:
        self.key = re.sub(r'[\.\-]', '', self.key)
        if len(self.key) != 11 or \
                not self.key.isdigit() \
                or self.key == self.key[::-1]:
            return False
        d1 = 11 - (sum(
            [int(d) * (10 - i) for i, d in enumerate(self.key[:9])]
        ) % 11)
        d1 = 0 if d1 > 9 else d1
        d2 = 11 - (sum(
            [int(d) * (11 - i) for i, d in enumerate(self.key[:10])]
        ) % 11)
        d2 = 0 if d2 > 9 else d2
        return self.key[-2:] == f'{d1}{d2}'
    def __testAndFormatKeyBRPhone(self) -> bool:
        if re.match(
            r'\(\d{2}\)\d{4,5}\-\d{4}', self.key
        ) != None:
            self.key = re.sub(r'[\(\-\)]', '', self.key)
            print(self.key)
            if '+55' not in self.key:
                self.key = f'+55{self.key}'
            return True
        return False
    def __testAndFormatKeyEmail(self) -> bool:
        return re.match(
            r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+', 
            self.key
        ) != None
    def __testRandkey(self) -> bool:
        return len(self.key) == 36
    def __validates(self):
        test = {
            PixType.CPF: self.__testAndFormatKeyCPF,
            PixType.CNPJ: self.__testAndFormatKeyCNPJ,
            PixType.BRPHONE: self.__testAndFormatKeyBRPhone,
            PixType.EMAIL: self.__testAndFormatKeyEmail,
            PixType.RANDKEY: self.__testRandkey,
        }
        if not test[self.type]():
            raise PixInvalidKeyException(
                extra=f'Key was not identified as "{self.type}"'
            )
    def toData(self) -> 'Data':
        return Data(1, self.key)

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
    pix = Pix()
    pix.setMname(fullname)
    pix.setMaiKey(PixKeyURI(key).toData(), description)
    pix.setMcity(city)
    pix.setTamount(value)
    if pix_id:
        pix.setPixID(pix_id)
    else:
        pix.setPixID(''.join(random.choice(
            string.ascii_uppercase + string.digits) 
            for _ in range(25)
        ))
    if pcode:
        if 0 < len(pcode) < 100:
            pix.payload['pcode'] = Data(61, pcode)
        else:
            raise PixInvalidPayloadException(
                extra="pcode length must be [1..99]"
            )
    pix.setMultipleTransaction(mult_transaction)
    return pix
