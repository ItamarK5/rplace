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
    return render_template('place.html', paint=json.loads(current_user.settings))


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
    form = SettingForm()
    settings = json.loads(current_user.settings)
    return render_template('accounts/profile.html', settings=settings)


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    print(form.__doc__)
    if form.validate_on_submit():
        # first search
        field = filter(lambda field:field.data is not None, form.__iter__())
    # else
