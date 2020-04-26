from flask import render_template, Response, jsonify
from flask_login import login_required, current_user

from painter.others.utils import auto_redirect
from painter.backends.extensions import storage_sql
from .forms import PreferencesForm
from . import place_router
from flask import request


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    """
    :return: view for the main application
    """
    if not current_user:
        return render_template('place.html')
    return render_template('place.html')


@place_router.route('/home', methods=('GET',))
@login_required
def home() -> Response:
    """
    :return: return the home page
    """
    return render_template('home.html')


@place_router.route('/profile', methods=('GET',))
@login_required
def profile() -> Response:
    """
    :return: profile page
    """
    form = PreferencesForm()
    return render_template(
        'profiles/profile.html', xstart=current_user.x, ystart=current_user.y,
        scalestart=current_user.scale, colorstart=current_user.color, form=form,
        chaturl=current_user.url
    )


@place_router.route('/preferences-submit', methods=("POST",))
@login_required
def profile_ajax():
    """
    view function that process a POST request from client
    thr url is for submitting a form request related
    to change a preference value by the user
    """
    form = PreferencesForm()
    if form.validate_on_submit():
        # you can only set 1 preference at a time
        # detecting the key \ val of the submitted form
        key, val = form.safe_first_hidden_fields()
        # why we dont have switch
        if key == 'url':
            current_user.url = val if val else None
        elif key == 'x':
            current_user.x = val
        elif key == 'y':
            current_user.y = val
        elif key == 'scale':
            current_user.scale = val
        elif key == 'color':
            current_user.color = val
        else:
            # otherwise set key as null
            key = None
        # save check in user
        if key is not None:
            storage_sql.session.add(current_user)
            storage_sql.session.commit()
            # https://stackoverflow.com/a/26080784
            return jsonify({'success': True, 'id': key, 'val': val})
        else:
            # return errors
            return jsonify({
                'success': False,
                'errors': ['Not valid parameter {}'.format(key)]
            })
    # return errors
    return jsonify({
        'success': False,
        'errors': next(iter(form.errors.values()))
    })
    # else


# force redirect to home
place_router.add_url_rule('/', 'home-redirect', auto_redirect('/home'), methods=('GET',))
