from flask_security import Security, SQLAlchemyUserDatastore
from painter.models.user import User, Role
from ..extensions import db
from wtforms import Form
<<<<<<< HEAD
from typing import Dict, Any, Optional


=======
>>>>>>> parent of cc4db7e... 2.4.2

datastore = SQLAlchemyUserDatastore(
    db=db,
    user_model=User,
    role_model=Role
)

<<<<<<< HEAD
class Security2(Security):
    def __find_form(self, kwargs:Dict[str, Any]) -> Optional[Form]:
        for val in kwargs.values():
            if isinstance(val, Form):
                return val
        return None

    def render_template(self, *args, **kwargs):
        form = self.__find_form(kwargs)
        if form is not None:
            kwargs['form'] = form
=======

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
>>>>>>> parent of cc4db7e... 2.4.2
        return super(Security2, self).render_template(*args, **kwargs)


security = Security2()
