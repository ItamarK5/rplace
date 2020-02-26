from __future__ import annotations
import warnings
from typing import Optional, Any, Dict
from flask import Flask
from firebase_admin import initialize_app, credentials


class Firebase:
    ext = None    # the building object

    def __init__(self, app: Optional[Flask] = None) -> None:
        if self.ext is None:
            self.app = app
            self.interface = None
            if app is not None:
                self.init_app(app)
            self.ext = self
        else:
            raise RuntimeError('You try making a app when you already made one')

    def init_app(self, app: Flask) -> None:
        self.app = app
        pth = self.get_config('FIRBASE_CERTIFICATE_PATH')
        if pth is None:
            warnings.warn('You must have a Certficate or the app wont work')
        else:
            certificate = credentials.Certificate('certificate.json')
            self.interface = initialize_app(certificate, options=self._get_admin_options())

    def _set_if_any(self, config_key: str, dict_key:str, dictionary: Dict[str, Any]) -> None:
        """
        :param dictionary: dictionary to set value
        :param dict_key: a dictionary key
        :param config_key: matched config key
        :return:
        """
        val = self.get_config(config_key)
        if val is not None:
            dictionary[dict_key] = val

    def _get_admin_options(self):
        admin_options = {}
        self._set_if_any('FIREBASE_DATABASE_URL', 'databaseURL', admin_options)

    def get_config(self, key: str) -> Any:
        return self.app.config.get(key, None)