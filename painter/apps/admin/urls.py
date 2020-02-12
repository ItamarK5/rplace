from flask import Blueprint, render_template, request, abort
from os.path import join as join_path
from painter.functions import admin_only
from .filters import *  # also import User class
from flask_login import fresh_login_required

admin_router = Blueprint(
    'admin',
    'admin',
)

admin_router.add_app_template_filter(draw_time, 'draw_time')
admin_router.add_app_template_filter(is_admin, 'is_admin')


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
    return render_template('admin/admin.html', pagination=pagination)


"""
@admin_router.route('/edit/<user_id:int>', methods=('GET',))
@admin_only
def admin_only(user_id:int) -> str:
    user = User.query.get(id=user_id).first()
    if user 
"""