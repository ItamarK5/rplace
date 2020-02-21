from os.path import join as path_join

from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required, current_user
import json
from painter.constants import WEB_FOLDER
from .forms import SettingForm
from painter.extensions import db

place_router = Blueprint('place', 'place',
                         static_folder=path_join(WEB_FOLDER, 'static'),
                         template_folder=path_join(WEB_FOLDER, 'templates'))


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    if not current_user:
        return render_template('place.html')
    return render_template('place.html', x=current_user.x, y=current_user.y, scale=current_user.scale,
                           color=current_user.color, url=current_user.url)


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
    return render_template(
        'accounts/profile.html', xstart=current_user.x, ystart=current_user.y,
        scalestart=current_user.scale, colorstart=current_user.color, form=form,
        chaturl=current_user.url
    )


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
        # first search
        # get form_fields
        form_fields = dict([
            (field.id, field.data) for field in form.__iter__()
            if field.raw_data and field.id not in form.errors
        ])
        print(form_fields)
        if 'x' in form_fields:
            current_user.x = form_fields['x']
        if 'y' in form_fields:
            current_user.y = form_fields['y']
        if 'scale' in form_fields:
            current_user.scale = form_fields['scale']
        if 'color' in form_fields:
            current_user.color = form_fields['color']
        if 'url' in form_fields:
            current_user.url = form_fields['url'] if form_fields['url'] not in ('', 'None') else None
        db.session.add(current_user)
        db.session.commit()
        # https://stackoverflow.com/a/26080784
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    print(form.errors)
    return json.dumps({'success': False, 'errors': form.errors}), 500, {'ContentType': 'application/json'}
    # else
