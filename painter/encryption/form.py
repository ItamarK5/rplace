import warnings
from typing import Any, Union
from typing import Optional

from flask_wtf.form import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict

from .flask_encrypt import FlaskEncrypt


def decrypt_form(pair):
    return pair[0], FlaskEncrypt.get_ext().decrypt_text(pair[1])


class EncryptedForm(FlaskForm):
    class Meta(FlaskForm.Meta):
        def wrap_formdata(self, form: Any, formdata: Any) -> Optional[Union[CombinedMultiDict, ImmutableMultiDict]]:
            data = super().wrap_formdata(form, formdata)
            if data is None:
                return None
            if isinstance(data, CombinedMultiDict):
                return CombinedMultiDict(
                    map(
                        lambda dictionary: dict(map(
                            decrypt_form,
                            dictionary.items()
                        )),
                        data.dicts
                    ))
            elif isinstance(data, ImmutableMultiDict):
                data = ImmutableMultiDict(dict(map(
                  decrypt_form, data.items()
                )))
                return data
            # else
            warnings.warn(f'Type {type(data)} not supported')
