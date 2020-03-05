import warnings
from typing import Any, Union, Optional, Dict

from flask_wtf.form import FlaskForm
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict

from .flask_encrypt import FlaskEncrypt


_SKIP = object()


def decrypt_val(encrypted_val:str) -> Union[str, type(_SKIP)]:
    val = FlaskEncrypt.get_ext().safe_decrypt(encrypted_val)
    return val if val is not None and val[0] else _SKIP


def decrypt_dictionary(dictionary: Dict[str, str]) -> Dict[str, str]:
    ret = {}
    for (key, val) in dictionary.items():
        dval = decrypt_val(val)
        if dval is not _SKIP:
            ret[key] = dval
    return ret


class EncryptedForm(FlaskForm):
    class Meta(FlaskForm.Meta):
        @staticmethod
        def get_encryption_key():
            return FlaskEncrypt.get_ext().public_key

        def wrap_formdata(self, form: Any, formdata: Any) -> Optional[Union[CombinedMultiDict, ImmutableMultiDict]]:
            data = super().wrap_formdata(form, formdata)
            # prevent errors
            return data
            """
                if data is None:
                    return None
                if isinstance(data, CombinedMultiDict):
                    return CombinedMultiDict(map(decrypt_dictionary, data.dicts))
                elif isinstance(data, ImmutableMultiDict):
                    data = ImmutableMultiDict(decrypt_dictionary(data))
                    return data
                # else
                warnings.warn(f'Type {type(data)} not supported')
            """

