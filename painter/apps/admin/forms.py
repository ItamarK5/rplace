from flask_wtf import *
from flask_wtf import form
from wtforms import TextAreaField, validators, BooleanField, DateTimeField, ValidationError
from datetime import timedelta, datetime

class BanForm(FlaskForm):
    set_active = BooleanField('active')
    expires = DateTimeField(
        'expires',
        format='%d/%m/%Y %H:%M',
        validators=[
            validators.Optional()
        ],
        render_kw={
            'data-target': "#expires",
            'data-toggle': 'datetimepicker'
        }
    )
    reason = TextAreaField('reason')

    def validate_expires(self, field):
        # get field data
        now = datetime.now()
        if field.data < now:
            raise ValidationError("You must select a day in the future, now now")
        if field.data - timedelta(minutes=5):
            raise ValidationError('Time must at least be higher then 5 minute from now')