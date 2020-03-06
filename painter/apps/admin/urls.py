from flask import Blueprint, render_template, abort, request, url_for, redirect
from flask.wrappers import Response
from flask_login import current_user
from painter.filters import *  # also import User class
from painter.models.user import reNAME
from painter.utils import admin_only
from painter.backends import lock

admin_router = Blueprint(
    'admin',
    'admin',
)


@admin_router.after_request
def add_header(response: Response) -> Response:
    # https://stackoverflow.com/a/34067710
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@admin_router.route('/admin', methods=('GET',))
@admin_only
def admin() -> str:
    """
    :return: return's admin template
    """
    pagination = User.query.paginate(per_page=1, max_per_page=20)
    # try get page
    page = request.args.get('page', '1')
    if not page.isdigit():
        abort(400, 'Given page isn\'t a number', description='Are you mocking this program? you'
                                                             ' an admin tries to edit the url')
    page = int(page)
    if not 1 <= page:
        abort(404, 'Page index too small')
    elif page > pagination.pages:
        abort(404, 'Page Number Not Found')
    return render_template('accounts/admin.html', pagination=pagination)


@admin_router.route('/edit/<string:name>', methods=('GET',))
@admin_only
def edit_user(name: str) -> str:
    """
    :param: name of user
    :returns: the web-page of the user
    """
    if reNAME.match(name) is None:
        abort(400, 'Name isn\'t good')
    user = User.query.filter_by(username=name).first_or_404()
    if user == current_user:
        abort(403)
        return redirect(url_for('place.profile'))
    if not current_user.is_superior_to(user):
        # forbidden error
        abort(403, f"You are not allowed to edit the user {user.username}")
    return render_template('accounts/edit.html', user=user)


@admin_router.route('/admin-power-button', methods=('GET',))
@admin_only
def set_admin_button():
    """
        view for the admin power button request (by ajax)
        to turn off == 1
        to turn on == 0
        query_string is in binary for some reason
    """
    if request.query_string == b'1':
        lock.enable()
    else:
        lock.disable()

