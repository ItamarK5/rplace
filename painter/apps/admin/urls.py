from flask import Blueprint, render_template, request, abort
from flask_login import fresh_login_required

from painter.functions import admin_only
from painter.models.user import reNAME
from .filters import *  # also import User class

admin_router = Blueprint(
    'admin',
    'admin',
)

admin_router.add_app_template_filter(draw_time, 'draw_time')
admin_router.add_app_template_filter(is_admin, 'is_admin')
admin_router.add_app_template_filter(role_icon, 'role_icon')
admin_router.add_app_template_filter(role_title, 'role_title')


@admin_router.route('/admin', methods=('GET',))
@admin_only
@fresh_login_required
def admin() -> str:
    """
    :return: return's admin template
    """
    pagination = User.query.paginate(per_page=1, max_per_page=20)
    # try get page
    print(pagination.pages, pagination.page)
    page = request.args.get('page', '1')
    if not page.isdigit():
        abort(400, 'given page isn\'t a number')
    page = int(page)
    if not 1 <= page <= pagination.pages:
        abort(400, 'page overflow')
    return render_template('accounts/admin.html', pagination=pagination)


@admin_router.route('/edit/<string:name>', methods=('GET',))
@admin_only
def admin_only(name: str) -> str:
    if reNAME.match(name) is None:
        abort(400, 'Name isn\'t good')
    user = User.query.filter_by(username=name).first_or_404()
    return render_template('accounts/edit.html', user=user)


@admin_router.after_request
def add_header(r):
    # https://stackoverflow.com/a/34067710
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
