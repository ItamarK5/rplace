from painter.constants import UserModel
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField
from wtforms.widgets import TextArea
from ..extensions import db


class UserView(ModelView):
    column_exclude_list = ['Pixels']
    can_delete = False
    can_edit = False
    can_create = False
    column_export_exclude_list = ('pixels',)



user_view = ModelView(UserModel, db.session)