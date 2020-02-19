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
def profile():
    form = SettingForm()
    settings = json.loads(current_user.paint_attrs)
    form.x_start.default = settings['x_start']
    form.y_start.default = settings['y_start']
    form.scale.default = settings['scale']
    form.colors.default = settings['color']
    form.url.default = settings['url'] if settings['url'] else ''
    form.process()  # https://stackoverflow.com/a/29544930
    return render_template('accounts/profile.html', form=form)


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
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
