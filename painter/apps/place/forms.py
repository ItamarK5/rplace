from typing import Tuple, Optional, Any

from flask_wtf import FlaskForm
from wtforms import fields, validators
from wtforms.compat import text_type as text_field_types
from wtforms.fields.html5 import IntegerField
from wtforms.widgets import HiddenInput

from painter.others.constants import COLORS


class PreferencesForm(FlaskForm):
    """
    Preference form
    handling validating changes in the user preferences
    """
    x = fields.html5.IntegerRangeField(
        'X start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='axis out of range')
        ],
        render_kw = {
            'min': 0,
            'max': 999
        }
    )

    y = IntegerField(
        'Y start',
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, max=999, message='coord out of range')
        ],
        render_kw={
            'min': 0,
            'max': 999
        }
    )

    scale = fields.html5.IntegerRangeField(
        'Scale start',
        default=None,
        validators=[
            validators.Optional(),
            validators.NumberRange(min=1, max=50, message='axis out of range')
        ],
        render_kw={
            'min': 1,
            'max': 50
        }
    )

    color = fields.SelectField(
        label='Select Color',
        coerce=int,
        choices=tuple(
            [(i, COLORS[i].title()) for i in range(len(COLORS))]
        ),
        validators=[
            validators.Optional(),
        ]
    )

    chat_url = fields.StringField(
        label='Chat URL',
        validators=[
            validators.Optional(),
            validators.URL(message="Not valid URL")
        ]
    )

    def safe_first_hidden_fields(self) -> Tuple[Optional[str], Optional[Any]]:
        """
        :return: the fields that arent hidden
        inspired by flask_wtf.form.hidden_tag
        """
        for f in self.__iter__():
            if isinstance(f, text_field_types):
                f = getattr(self, f, None)

            if f is None or isinstance(f.widget, HiddenInput) \
                    or (not f.raw_data) or f.id in self.errors:
                continue
            return f.id, f.data
        return None, None
