from flask import Flask
from itsdangerous import URLSafeTimedSerializer
# https://realpython.com/handling-email-confirmation-in-flask/

class TokenSerializer:
    signup: URLSafeTimedSerializer

    @classmethod
    def init_app(cls, app:Flask) -> None:
        """
        :param app: the Application object
        :return: None
        initilize the token serializer
        """
        cls.signup = URLSafeTimedSerializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['SECURITY_PASSWORD_SALT']
        )
