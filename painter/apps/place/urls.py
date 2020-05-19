from flask import render_template, Response, jsonify
from flask_login import login_required, current_user

from painter.backends.extensions import storage_sql
from painter.others.utils import auto_redirect
from .forms import PreferencesForm
from .router import place_router
from .utils import update_user_preferences


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    """
    :return: view for the main application
    """
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
        'profiles/profile.html', form=form,
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
        # why we don't have switch
        preference_field = update_user_preferences(form)
        if preference_field is None:
            # otherwise set key as null
            return jsonify({
                'success': False,
                'errors': ['You passed no valid value']
            })
        # save check in user
        storage_sql.session.add(current_user)
        storage_sql.session.commit()
        # https://stackoverflow.com/a/26080784
        return jsonify({'success': True, 'id': preference_field.id, 'val': preference_field.data})
    # return errors
    return jsonify({
        'success': False,
        'errors': next(iter(form.errors.values()))
    })


# else


# force redirect to home
place_router.add_url_rule('/', 'home-redirect', auto_redirect('/home'), methods=('GET',))
