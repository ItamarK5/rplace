from flask_wtf import *
from flask_wtf import form
from wtforms import DateTimeField, TextAreaField, validators, BooleanField


class BanForm(FlaskForm):
    set_active = BooleanField('active')
    expired = DateTimeField(
        'expires',
        validators=[
            validators.Optional()
        ],
        render_kw={'data-target': "#data-time-picker"}
    )
    reason = TextAreaField('reason')