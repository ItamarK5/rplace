from __future__ import annotations

import warnings
from typing import Optional

from flask import Flask

__FLASK_ENCRYPT_APP__ = None

_SIMPLE_PRIVATE_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDlOJu6TyygqxfWT7eLtGDwajtN" \
                      "FOb9I5XRb6khyfD1Yt3YiCgQWMNW649887VGJiGr/L5i2osbl8C9+WJTeucF+S76" \
                      "xFxdU6jE0NQ+Z+zEdhUTooNRaY5nZiu5PgDB0ED/ZKBUSLKL7eibMxZtMlUDHjm4" \
                      "gwQco1KRMDSmXSMkDwIDAQAB".encode()

_SIMPLE_PUBLIC_KEY = "MIICXQIBAAKBgQDlOJu6TyygqxfWT7eLtGDwajtNFOb9I5XRb6khyfD1Yt3YiCgQWMNW6" \
                     "49887VGJiGr/L5i2osbl8C9+WJTeucF+S76xFxdU6jE0NQ+Z+zEdhUTooNRaY5nZiu5Pg" \
                     "DB0ED/ZKBUSLKL7eibMxZtMlUDHjm4gwQco1KRMDSmXSMkDwIDAQABAoGAfY9LpnuWK5Bs" \
                     "50UVep5c93SJdUi82u7yMx4iHFMc/Z2hfenfYEzu+57fI4fvxTQ//5DbzRR/XKb8ulNv6+C" \
                     "HyPF31xk7YOBfkGI8qjLoq06V+FyBfDSwL8KbLyeHm7KUZnLNQbk8yGLzB3iYKkRHlmUanQGaN" \
                     "MIJziWOkN+N9dECQQD0ONYRNZeuM8zd8XJTSdcIX4a3gy3GGCJxOzv16XHxD03GW6UNLmfPwenKu" \
                     "+cdrQeaqEixrCejXdAFz/7+BSMpAkEA8EaSOeP5Xr3ZrbiKzi6TGMwHMvC7HdJxaBJbVRfApFrE0/m" \
                     "PwmP5rN7QwjrMY+0+AbXcm8mRQyQ1+IGEembsdwJBAN6az8Rv7QnD/YBvi52POIlRSSIMV7SwWvSK4" \
                     "WSMnGb1ZBbhgdg57DXaspcwHsFV7hByQ5BvMtIduHcT14ECfcECQATeaTgjFnqE/lQ22Rk0eGaYO80" \
                     "cc643BXVGafNfd9fcvwBMnk0iGX0XRsOozVt5AzilpsLBYuApa66NcVHJpCECQQDTjI2AQhFc1yRnC" \
                     "U/YgDnSpJVm1nASoRUnU8Jfm3Ozuku7JUXcVpt08DFSceCEX9unCuMcT72rAQlLpdZir876".encode()


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
        self.__app.config.setdefault('CRYPT_PRIVATE_KEY', _SIMPLE_PRIVATE_KEY)
        self.__app.config.setdefault('CRYPT_PUBLIC_KEY', _SIMPLE_PUBLIC_KEY)
        self.__private_key = self.__app.config['CRYPT_PRIVATE_KEY']
        self.__public_key = self.__app.config['CRYPT_PRIVATE_KEY']
        self.__app.extensions['FLASK_ENCRYPT'] = self

    def encyrpt_text(self, text: str) -> str:
        pass

    def decrypt_text(self, text: str) -> str:
        pass

    @property
    def private_key(self):
        return self.__app.config.get('CRYPT_PRIVATE_KEY')

    @property
    def public_key(self):
        return self.__app.config.get('CRYPT_PUBLIC_KEY')
