from datetime import datetime, timedelta

from flask_wtf import *
from wtforms import TextAreaField, validators, BooleanField, DateTimeField, ValidationError


class RecordForm(FlaskForm):
    """
    Form to vaildate a new record object
    """
    set_banned = BooleanField('active')
    affect_from: DateTimeField = DateTimeField(
        'affect from',
        format='%d/%m/%Y %H:%M',
        validators=[
            validators.Optional(),
        ],
        render_kw={
            'data-target': "#affect_from",
            'data-toggle': 'datetimepicker',
            'aria-label': 'date to start the effect'
        }
    )
    reason = TextAreaField(
        'reason',
        [
            validators.required(),
            validators.length(-1, 512, message="The reason must be less or equal to 512 characters"),
        ],
    )
    note_description = TextAreaField(
        'description',
        [
            validators.required(),
            validators.length(-1, 512, message="a description must be less or equal to 512 characters"),
        ],
    )

    def validate_affect_from(self, field: DateTimeField) -> None:
        """
        :param field: the affect_from field
        :return None
        validates if the new date would is dated at least 1 minute after task created
        """
        # get field data
        if field.data is not None:
            #
            if datetime.now() > field.data + timedelta(minutes=1):
                raise ValidationError("You must select a day in the future, not now")


class NoteForm(FlaskForm):
    """
    Form to vaildate a new note model
    """
    description = TextAreaField(
        'description',
        [
            validators.required(),
            # note max size is 512
            validators.length(-1, 512, message="a description must be less then 256 characters"),
        ],
    )
