import warnings
from typing import Optional, Any, Dict
from flask import Flask
from firebase_admin import initialize_app, credentials
from .helpers.classproperty import ClassPropertyMetaClass, class_property


class Firebase(metaclass=ClassPropertyMetaClass):
    __app = None    # the building object

    def __init__(self, app: Optional[Flask] = None) -> None:
        if self.__app is None:
            self.app = app
            self.interface = None
            if app is not None:
                self.init_app(app)
            self.__app = self
        else:
            raise RuntimeError('You try making a app when you already made one')

    def init_app(self, app: Flask) -> None:
        self.app = app
        pth = self.__getconfig('FIRBASE_CERTIFICATE_PATH')
        if pth is None:
            warnings.warn('You must have a Certficate or the app wont work')
        else:
            certificate = credentials.Certificate('certificate.json')
            self.interface = initialize_app(certificate, options=self.__get_admin_options())

    def set_if_any(self, config_key: str, dict_key:str, dictionary: Dict[str, Any]) -> None:
        """
        :param dictionary: dictionary to set value
        :param dict_key: a dictionary key
        :param config_key: matched config key
        :return:
        """
        val = self.__getconfig(config_key)
        if val is not None:
            dictionary[dict_key] = val

    def __get_admin_options(self):
        admin_options = {}
        self.set_if_any('FIREBASE_DATABASE_URL', 'databaseURL', admin_options)

    def __getconfig(self, key: str) -> Any:
        return self.app.config.get(key, None)

    @class_property
    def ext(self):
        return self.__app