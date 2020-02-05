from flask_security import Security, SQLAlchemyUserDatastore
from painter.models.user import User, Role
from ..extensions import db

datastore = SQLAlchemyUserDatastore(
    db=db,
    user_model=User,
    role_model=Role
)

security = Security(datastore=datastore)


def init_security(app):
    security.init_app(app, datastore)
