class PixInvalidPayloadException(Exception):
    def __init__(self,
        message:str='The Pix payload is invalid.',
        extra:str=''):
        self.message = f'{message} {extra}'
        super().__init__(self.message)

class PixInvalidKeyException(Exception):
    def __init__(self,
        message:str='The Pix key is invalid.',
        extra:str=''):
        self.message = f'{message} {extra}'
        super().__init__(self.message)

class QRCodeInvalidFilepath(Exception):
    def __init__(self,
        message:str='Invalid filepath to write qrcode.',
        extra:str=''):
        self.message = f'{message} {extra}'
        super().__init__(self.message)