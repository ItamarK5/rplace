from __future__ import annotations
import os
import rsa
import warnings
from typing import Optional, Tuple

from flask import Flask


_SIMPLE_PRIVATE_KEY = '-----BEGIN RSA PRIVATE KEY-----\n'\
                     'MIIJNgIBAAKCAgEApskpQoRukk/3d/0m6CZzl8tSpn6rhjicsMWZKqFbnvEpNHKh\n'\
                     'IUy6zKob4+1vvLV3ftJw5GKk9xJ9NtmU9LAWbb7383qGjjogVyqGt/FdD9RlVN3j\n'\
                     'nxpm+wTfzaWZI0DJKUWglkxgHTc1YcnEzueOyQFs/AwrsDKbBrLovipZVNPxbCO/\n'\
                     'xhRteNEXMrudy3Yny9fm3PuBFIGDzFPVF4gRz/GqORMm0CAA+l6HK+RA1oe4BU9p\n'\
                     'CZhQ0C4pILL+xChAloNTmwHe/dxLWHK3Q/plMWwKkE9GO8uCaH3J1MiuUULzsGr3\n'\
                     'IOHPYZ9frM/u1Gfk2JkdRvUBCO+VHnEP2O7TMYJbnvlrFwDxEZoJYRrGh4s5n11k\n'\
                     'rMOXfyamikGXS/AOnEwHMeojTKteEnmGMVFNJPlX1awnLRL+i/+PRBXJUAA1UQCa\n'\
                     'l9QAMPHSP6Wo1brKTQGzx3xhtjE/V49DC9dh/NYsw4Teq/6oYfdIISBMMCpMa3DQ\n'\
                     'kBy8ZQ2whanD2ju+rH5+tTcf7RS+7rHTbBhTlEsFqTrRntqRbYUEfPBwXt+YQMnQ\n'\
                     'ljX0PzWawIJ2PeDzZnwkjYekuPmDZyQT6xo2T0LQBceuobpHqfrIJNmJlH9nShgG\n'\
                     'w5PcmXy7w3FPtQ6SfKzdbQGwm69mZuC6oXcrvIuk3NHYw6k42SaW0hN3HiMCAwEA\n'\
                     'AQKCAgB6pPHyN/AXJzaSxVUW4S+fL6RXSk5XJMoUMzmuX3lAJ5ZlOuXB1uqGFZDs\n'\
                     'ymygF9EHMThSuTcVeEMbUmR2igX0LbmnETJg491kO6FVIeeM/GKHRaNcG84eSDdK\n'\
                     'wbsacUl7T/gGjaMf2Lkob3aJrz0QEjxSG6EEsDHPe0AqlnmaJ0AghSlAP0VA0oB8\n'\
                     'jfo642fgPaNGXKtOqO6CEiNgam6uusaxsaOY5+/QLDK5097Z4nMvdHWI2LiUXV1g\n'\
                     '7j7pf6/+/hM8qOORSa0eHT0mf7pp3UjnVWQQFFaQ/+6qyedlWhZYZE/VnjchUlDI\n'\
                     'gx7ckojOkk/mTEhLFtSdfKuuL4ba6iFc0ENZXO8qHkK71F5ziVdKaASJx6tpkYho\n'\
                     'eX9/YUKEBGTJTyByZ6I0GMedXVrUDDLYP3I1wnPdEkWFOOOxk2FlgZU0hOYLmIl6\n'\
                     'bj9jKsywwh0KttI+2eYJEH9nqPpyRZ6G94frY40i4ynMOnPn/LxPNYHVA0E8+Xc/\n'\
                     '+XRs3psEmjxvhn5WZnp88kLmmJt+VfLWn1Gc4UHhjDMnvCe/hXzePVg4bbQ3Omnn\n'\
                     '/osI2Pq/JdjFBcqbDSeQ4Rzq1uV2fJcP2WZGX5zbIzj69M6pM2G1I2EOR7uWAid3\n'\
                     'YUiNCkipOMFxyW/Yqy7oaj9NlqW/Qkr5TXulYQpfW/+IUJ6kAQKCAREA41VMO5aV\n'\
                     'eqlhKj+3kQ3SHjXiNq3F+0tZvjylSd0Zx+yvrRncuCS5AKGFyTyz2vPrL7nNfcbz\n'\
                     'hn74cq6n/mJWB+uC1V+xrKfG7lXo931izWtB1chXOF1yus+QikijnEOvFWnQFpLx\n'\
                     '/5YTdX0OnT76fZqZsahg0UERIMPIUfwTVr61G4iScJ9uE7s93D5wBRB5X8/dL4ef\n'\
                     '7l90WO19RrgBZNfYgIxEhYdNLBcL6SBlYgN2RkTUPnekXCX9ka9taeG4IfVUhocX\n'\
                     'bcP85n7UacBF3R0fng8HKPpFOHpSKDNZWlxlYrmZdTSfM2MC9E7NNIFKVg2oz50T\n'\
                     'K90MlOacyTjoITLdFTx6IDtCBS2JJJ96QusCgfEAu9FKQEvtzOTeRoXahPdwvTvr\n'\
                     'FOnq3oMn3ireROxc0XQ4SsdBhje5h66g922UyIltwNzyQbnB4rUJU6BUNsShWUkx\n'\
                     'e+5XbxaViTCnv4XWxzmJrdxeSEsKduxKjND9H9kpcYL6gr3j3BXa1v0iS3hBU7s7\n'\
                     'CNKBBRxuJa4B31z8W5Ut5owylkxkGhV/iiZuDF7fNi/tEXm1k1hxsLf1cNIbFxoy\n'\
                     'X0S3CN6hn4BCaZk21dtbrEJoIgiHC/2SCFrrJuNuw3kwwK0CCOKK8kyJ3LBjWY5O\n'\
                     'Z7mNkrdpmUqIscbJuHD6NqJlffxZpu6gfwko/JOpAoIBEGpV2L26txrUJbX8beH0\n'\
                     'xAcLj0+iQwxDd6vrdCkzub5xcM8YXMzpqHuqEglKUpqlI6qET6F4sSqFM7N5DO2J\n'\
                     'k9JKkD08cMBhDkUnfDxfsxqBBB96gYnE9Eh7lJGKXrVWV4w9nW8htv6ldV6sa2yU\n'\
                     'K9kauq+GIhtfQyK/UXE/5s/Zjp9dZ5o0iOnD2LCvp/hGd2+grEZyOxXmImcCV2n/\n'\
                     '4e8Io6Wldtu6qRdphFG8rI+HLQi7Y0gA8KmFv7EojJZNVbLUrX/rqsLWPPKX+sWo\n'\
                     'gUVnPQXS47eAMWa0mL9jHXWN6IKgbC6NubXwp04dmhDoNRxBcWgDghcvY5Y2tLnO\n'\
                     '243D2/P2AO4Yqc4AObkeu7KXAoHxALjRKEnA7c5T4M5w5Sk2/H+aOKgpzu8LDO44\n'\
                     'LOSR2nxZ6xLapIXYy/7SPp97+46ifZftU46NplbaYsUh3fzO3R8pQUJ8tRkhliCb\n'\
                     '+lYi88izu+GUGkr1XOTNfEa5WHxAi+GhS7Xf+hsWfnRUP60YNuCYO21hB4jqAxGc\n'\
                     '+0a7D7FnSPW3PAheP5rTUN+3FU+jA+8klho+NAk8XRPS0fklJ3dCVhMdYSefPFfi\n'\
                     'NHgJRsaGxtzps+LZlVqdOVhzbzajUtmTpf/Tv07S7nukCX1bLUhxGoJDOycGySkJ\n'\
                     'CR43SUTwF6gvgcPJ0MbNxq17bBOvkQKCARAa/J2jwmDkqO6ipBbMJ6a+1r0eqk6l\n'\
                     'c0F453yaWEw+sNv4IsBEqLLBjlhKeMKVUgkA1aZEsr7Iz5mluIIjX2iq3usU0dIQ\n'\
                     'IwztOau/6zTeII2mNmKp5kbC4B6lBp+IoZfyGVKEm4H7M0ftnc78KfQIS97WilpS\n'\
                     'Vn3uM9Dh5pMJfLr5jF9bswRNkNnby/p5dSpIkE7RIF/4RsU+vfHQHij7GQUR0AWc\n'\
                     'no9r/V9yCIf2o1HL3E7FEwrze8oDp1LdpoYDeTqJcA63O+D8hmPV8z5Y1XCvsiPG\n'\
                     'LsUfVNF5/AC2BMRz6OLIObrzq1QlmC7x1SyGbik/WlFncsvbkQDxBxTXEW5SdW0l\n'\
                     'tM8KDCS6CiMd7Q==\n'\
                     '-----END RSA PRIVATE KEY-----'

_SIMPLE_PUBLIC_KEY = '-----BEGIN RSA PUBLIC KEY-----\n'\
                     'MIICCgKCAgEApskpQoRukk/3d/0m6CZzl8tSpn6rhjicsMWZKqFbnvEpNHKhIUy6\n'\
                     'zKob4+1vvLV3ftJw5GKk9xJ9NtmU9LAWbb7383qGjjogVyqGt/FdD9RlVN3jnxpm\n'\
                     '+wTfzaWZI0DJKUWglkxgHTc1YcnEzueOyQFs/AwrsDKbBrLovipZVNPxbCO/xhRt\n'\
                     'eNEXMrudy3Yny9fm3PuBFIGDzFPVF4gRz/GqORMm0CAA+l6HK+RA1oe4BU9pCZhQ\n'\
                     '0C4pILL+xChAloNTmwHe/dxLWHK3Q/plMWwKkE9GO8uCaH3J1MiuUULzsGr3IOHP\n'\
                     'YZ9frM/u1Gfk2JkdRvUBCO+VHnEP2O7TMYJbnvlrFwDxEZoJYRrGh4s5n11krMOX\n'\
                     'fyamikGXS/AOnEwHMeojTKteEnmGMVFNJPlX1awnLRL+i/+PRBXJUAA1UQCal9QA\n'\
                     'MPHSP6Wo1brKTQGzx3xhtjE/V49DC9dh/NYsw4Teq/6oYfdIISBMMCpMa3DQkBy8\n'\
                     'ZQ2whanD2ju+rH5+tTcf7RS+7rHTbBhTlEsFqTrRntqRbYUEfPBwXt+YQMnQljX0\n'\
                     'PzWawIJ2PeDzZnwkjYekuPmDZyQT6xo2T0LQBceuobpHqfrIJNmJlH9nShgGw5Pc\n'\
                     'mXy7w3FPtQ6SfKzdbQGwm69mZuC6oXcrvIuk3NHYw6k42SaW0hN3HiMCAwEAAQ==\n'\
                     '-----END RSA PUBLIC KEY-----'


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
            keys = rsa.newkeys(1024)
            _SIMPLE_PRIVATE_KEY = keys[1].save_pkcs1()
            _SIMPLE_PUBLIC_KEY = keys[0].save_pkcs1()

    def init_app(self, app: Flask) -> None:
        self.__app = app
        self.__init_app(app)

    @property
    def app(self) -> Flask:
        return self.__app

    def __init_app(self, app: Flask) -> None:
        self.__app = app
        self.__class__._ext = self
        private_key = self.__app.config.get('CRYPT_PRIVATE_KEY', _SIMPLE_PRIVATE_KEY)
        if os.path.exists(private_key) and os.path.isfile(private_key):
            with open(private_key, 'web') as filekey:
                private_key = filekey.read()
        self.__private_key = rsa.PrivateKey.load_pkcs1(private_key)
        # load public key
        public_key = self.__app.config.get('CRYPT_PUBLIC_KEY', _SIMPLE_PUBLIC_KEY)
        if os.path.exists(public_key) and os.path.isfile(public_key):
            with open(private_key, 'web') as filekey:
                public_key = filekey.read()
        self.__public_key = rsa.PublicKey.load_pkcs1(public_key)
        app.extensions['FLASK_ENCRYPT'] = self

    def encyrpt_text(self, text: str) -> str:
        return rsa.encrypt(text.encode(), pub_key=self.__public_key).decode()

    def decrypt_text(self, text: str) -> str:
        return rsa.decrypt(text.encode(), priv_key=self.__private_key).decode()

    def safe_decrypt(self, text: str) -> Optional[Tuple[bool, str]]:
        try:
            return True, self.decrypt_text(text)
        except rsa.DecryptionError:
            return False, 'Decrypt Error'
        except rsa.VerificationError:
            return False, 'Verify Error'
        finally:
            return None

    @property
    def private_key(self):
        return self.__private_key\
            .save_pkcs1()

    @property
    def public_key(self):
        return self.__public_key\
            .save_pkcs1()
