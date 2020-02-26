import warnings
from typing import Optional, Any
from flask import Flask
from firebase_admin import initialize_app, credentials


class FlaskFirebase:
    def __init__(self, app: Optional[Flask] = None) -> None:
        self.app = app
        self.interface = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.app = app
        pth = self.__getconfig('FIRBASE_CERTIFICATE_PATH')
        if pth is None:
            warnings.warn('You must have a Certficate or the app wont work')
        else:
            certificate = credentials.Certificate('certificate.json')
            self.interface = initialize_app(certificate)

    def __getconfig(self, key: str) -> Any:
        return self.app.config.get(key, None)
