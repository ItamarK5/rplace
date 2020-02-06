from flask_security import Security, SQLAlchemyUserDatastore
from painter.models.user import User, Role
from ..extensions import db
from wtforms import Form
from typing import Dict, Any, Optional



datastore = SQLAlchemyUserDatastore(
    db=db,
    user_model=User,
    role_model=Role
)

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
        return super(Security2, self).render_template(*args, **kwargs)


security = Security2()
