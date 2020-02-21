from __future__ import annotations
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.fields.html5 import IntegerRangeField


class SettingForm(FlaskForm):
    x = IntegerRangeField(
        'X start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='axis out of range')
        ],
    )
    y = IntegerRangeField(
        'Y start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='coord out of range')
        ],
    )
    scale = IntegerRangeField(
        'Scale start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=1, max=50, message='axis out of range')
        ],
    )
    color = IntegerField(
        validators=[
            validators.Optional(),
            validators.NumberRange(0, 16, 'Value not match')
        ]
    )

    url = StringField(
        'Chat URL',
        validators=[
            validators.Optional(),
            validators.URL(message="Not valid URL")
        ]
    )
