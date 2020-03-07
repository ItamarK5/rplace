from os.path import join as path_join

from flask import Blueprint, render_template, Response, jsonify
from flask_login import login_required, current_user
from painter.constants import WEB_FOLDER
from painter.extensions import db
from ..profile_form import SettingForm

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


@place_router.route('/preferences-submit', methods=("POST",))
@login_required
def profile_ajax():
    form = SettingForm()
    if form.validate_on_submit():
        key, val = form.safe_first_hidden_fields()
        if key == 'url':
            current_user.url = val if val != '' and val is not None else None
        elif key == 'x':
            current_user.x = val
        elif key == 'y':
            current_user.y = val
        elif key == 'scale':
            current_user.scale = val
        elif key == 'color':
            current_user.color = val
        else:
            key = None
        if key is not None:
            db.session.add(current_user)
            db.session.commit()
            # https://stackoverflow.com/a/26080784
            return jsonify({'success': True, 'id': key, 'val': val})
        else:
            return jsonify({
                'success': False,
                'errors': ['Not valid parameter {}'.format(key)]
            })
    return jsonify({
        'success': False,
        'errors': next(iter(form.errors.values()))
    })
    # else
