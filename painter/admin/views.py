from painter.constants import UserModel
from flask_admin.contrib.sqla import ModelView
from ..extensions import db


class UserView(ModelView):
    column_exclude_list = ['Pixels']
    can_delete = False
    can_edit = False
    column_export_exclude_list = ('pixels',)

    def after_model_change(self, form, model, is_created):
        super().after_model_change(form, model, is_created)
        pass



user_view = ModelView(UserModel, db.session)