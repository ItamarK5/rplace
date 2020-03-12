from flask_wtf import *
from wtforms import TextAreaField, validators, BooleanField, DateTimeField, ValidationError, Field
from datetime import datetime, timedelta


class RecordForm(FlaskForm):
    set_banned = BooleanField('active')
    expires: DateTimeField = DateTimeField(
        'expire',
        format='%d/%m/%Y %H:%M',
        validators=[
            validators.Optional(),
        ],
        render_kw={
            'data-target': "#expires",
            'data-toggle': 'datetimepicker',
            'aria-label': 'reason to ban/unban the player'
        }
    )
    reason = TextAreaField(
        'reason',
        [
            validators.required(),
            validators.length(-1, 256, message="The reason must be less then 256 characters"),
        ],
    )
    note = TextAreaField(
        'description',
        [
            validators.required(),
            validators.length(-1, 256, message="a description must be less then 256 characters"),
        ],
    )

    def validate_expires(self, field: DateTimeField) -> None:
        # get field data
        if field.data is not None:
            now = datetime.now()
            print(now, field.data)
            if now > field.data + timedelta(minutes=1):
                raise ValidationError("You must select a day in the future, now now")


class NoteForm(FlaskForm):
    description = TextAreaField(
        'description',
        [
            validators.required(),
            validators.length(-1, 256, message="a description must be less then 256 characters"),
        ],
    )