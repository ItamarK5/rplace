from __future__ import annotations
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import IntegerField


class SettingForm(FlaskForm):
    x = IntegerField(
        'X start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='axis out of range')
        ],
    )

    y = IntegerField(
        'Y start',
        default=None,
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='coord out of range')
        ],
    )
    scale = IntegerField(
        'Scale start',
        default=None,
        validators=[
            validators.Optional(),
            validators.NumberRange(min=1, max=50, message='axis out of range')
        ],
    )
    color = IntegerField(
        default=None,
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=15, message='Unknown color')
        ]
    )

    url = StringField(
        'Chat URL',
        default=None,
        validators=[
            validators.Optional(),
            validators.URL(message="Not valid URL")
        ]
    )
