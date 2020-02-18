from os.path import join as path_join

from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required, current_user

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
    return render_template('place.html', paint=current_user.paint_atts)


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
    return render_template('accounts/profile.html', form=form)


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
        return jsonify(valid=True)
    return jsonify(
        valid=False,
        **form.errors
    )