from flask import Blueprint, render_template
from os.path import join as join_path
from painter.functions import admin_only
from painter.models.user import User
from .filters import draw_time

admin_router = Blueprint(
    'admin',
    'admin',
)

admin_router.add_app_template_filter(draw_time, 'draw_time')


@admin_router.route('/admin', methods=('GET',))
@admin_only
def admin() -> str:
    """
    :return: return's admin template
    """

    pagination = User.query.paginate(1, 20)
    return render_template('admin/admin.html', pagination=pagination)
