from __future__ import annotations
from flask_wtf import FlaskForm
from wtforms import *


class SettingForm(FlaskForm):
    x = DecimalField('Question 1', validators=[validators.NumberRange(min=0, max=10, message='bla')])
