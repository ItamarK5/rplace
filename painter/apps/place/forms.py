from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import IntegerField

from painter.others.constants import COLORS


class PreferencesForm(FlaskForm):
    """
    Preference form
    handling validating changes in the user preferences
    """
    x = IntegerField(
        'X start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='axis out of range'),
        ],
    )

    y = IntegerField(
        'Y start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='coord out of range'),
        ],
    )
    scale = IntegerField(
        'Scale start',
        default=None,
        validators=[validators.Optional()]
    )
    color = SelectField(
        label='Select Color',
        coerce=int,
        choices=tuple(
            [(i, COLORS[i].title()) for i in range(len(COLORS))]
        ),
        validators=[validators.Optional()]
    )

    chat_url = StringField(
        label='Chat URL',
        validators=[
            validators.Optional(),
            validators.URL(message="Not valid URL")
        ]
    )
