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
    return render_template('accounts/profile.html', settings=settings, form=form)


@place_router.route('/settings-submit', methods=("POST",))
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
        # first search
        settings = json.loads(current_user.settings)
        # get form_fields
        form_fields = dict([(field.id, field.data) for field in form])
        print(form_fields)
        if form_fields['x'] is not None:
            settings['x'] = form_fields['x']
        if form_fields['y'] is not None:
            settings['y'] = form_fields['y']
        if form_fields['scale'] is not None:
            settings['color'] = form_fields['color']
        if form_fields['color'] is not None and form['color'] != 'None':
            settings['color'] = form_fields['color']
        if form_fields['url'] is not None:
            settings['url'] = form_fields['url']
        print(settings)
        current_user.settings = json.dumps(settings)
        db.session.add(current_user)
        db.session.commit()
        #https://stackoverflow.com/a/26080784
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    print(form.errors)
    return json.dumps({'success': False, 'errors':form.errors }), 500, {'ContentType': 'application/json'}
    # else
