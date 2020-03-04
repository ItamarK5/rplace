from __future__ import annotations
import os
import warnings
from typing import Optional, Tuple, Union
from flask import Flask
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


__all__ = ['FlaskEncrypt']


def load_rsa_key(rsa_key: Union[str, bytes]) -> str:
    if isinstance(rsa_key, str):
        if os.path.exists(rsa_key):
            if os.path.isfile(rsa_key):
                with open(rsa_key, 'rt') as rfile:
                    return rfile.read()
            else:
                raise OSError("Enter a file, not a folder")
        else:
            return rsa_key
    # else
    elif isinstance(rsa_key, bytes):
        return rsa_key.decode()


class FlaskEncrypt:
    _ext: Optional[FlaskEncrypt] = None

    @classmethod
    def get_ext(cls):
        if cls._ext is None:
            warnings.warn('Extension hasn\'t been initialized')
        return cls._ext

    def __init__(self, app: Optional[Flask] = None) -> None:
        if self._ext is not None:
            warnings.warn('Extension has already been created')
        if app is not None:
            self.__init_app(app)
        else:
            self.__private_key = None
            self.__public_key = None
            self.__encrypt = None
            self.__app = None

    def init_app(self, app: Flask) -> None:
        self.__app = app
        self.__init_app(app)

    @property
    def app(self) -> Flask:
        return self.__app

    def __init_app(self, app: Flask) -> None:
        self.__app = app
        self.__class__._ext = self
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()
        # load public key

        app.extensions['FLASK_ENCRYPT'] = self

    def encyrpt_text(self, text: str) -> str:
        return self.__public_key.encrypt(text)

    def decrypt_text(self, text:str) -> str:
        return self.__private_key.encrypt(text)

    def safe_decrypt(self, text:str) -> str:
        return self.decrypt_text(text)

    @property
    def private_key(self):
        return self.__private_key\
            .save_pkcs1()

    @property
    def public_key(self):
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

    """
    pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
 )
    """