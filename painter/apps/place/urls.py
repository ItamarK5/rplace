from os.path import join as path_join

from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required, current_user
import json
from painter.constants import WEB_FOLDER
from .forms import SettingForm

place_router = Blueprint('place', 'place',
                         static_folder=path_join(WEB_FOLDER, 'static'),
                         template_folder=path_join(WEB_FOLDER, 'templates'))


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    if not current_user:
        return render_template('place.html')
    return render_template('place.html', paint=json.loads(current_user.paint_attrs))


@place_router.route('/', methods=('GET',))
@login_required
def home() -> Response:
    """
    :return: return the home page
    """
    return render_template('home.html')


@place_router.route('/profile', methods=('GET',))
@login_required
def profile():
#    form = SettingForm()
    settings = json.loads(current_user.settings)
    return render_template('accounts/profile.html', settings=settings)


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.paint_attrs = json.dumps({
            'x_start':  form.x_start.data,
            'y_start':  form.y_start.data,
            'scale':    form.scale.data,
            'color':    form.color.data,
            'url':      form.url.data
        })
        return 200
    else:
        settings = json.loads(current_user.paint_attrs)
        errors = dict(form.errors)
        return jsonify(
            errors=list(errors.items()),
            values=[
                (field.id, settings[field.id] if settings[field.id] else '')
                for field in form.__iter__() if
                field.id != 'csrf_token' and field.id not in errors
            ]
        )
