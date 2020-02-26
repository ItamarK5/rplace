from abc import ABCMeta


class ModelMeta(ABCMeta):
    __database_reference__: str
    __cache_text__: str

    def __load__(cls):
        pass


class Model:
    def __init__(self):
        pass

    def search(self, ):
        pass
