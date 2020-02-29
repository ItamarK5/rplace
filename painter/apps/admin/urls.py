from flask import Blueprint, render_template, request, abort
from flask.wrappers import Response

from painter.filters import *  # also import User class
from painter.models.user import reNAME
from painter.utils import admin_only

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
    print(pagination.pages, pagination.page)
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
def edit_user(name: str) -> str:
    if reNAME.match(name) is None:
        abort(400, 'Name isn\'t good')
    user = User.query.filter_by(username=name).first_or_404()
    return render_template('accounts/edit.html', user=user)
