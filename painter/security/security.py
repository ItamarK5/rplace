from flask_security import Security, SQLAlchemyUserDatastore
from painter.models.user import User, Role
from ..extensions import db
from wtforms import Form

datastore = SQLAlchemyUserDatastore(
    db=db,
    user_model=User,
    role_model=Role
)


class Security2(Security):
    @staticmethod
    def __search_form(kwargs):
        for attr in kwargs.values():
            if isinstance(attr, Form):
                return attr
        return None

    def render_template(self, *args, **kwargs):
        if 'form' not in kwargs:
            form = self.__search_form(kwargs)
            if form is not None:
                kwargs['form'] = form
                print(dir(form))
        return super(Security2, self).render_template(*args, **kwargs)


security = Security2()
