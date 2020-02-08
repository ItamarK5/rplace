from flask import Blueprint, render_template
from os.path import join as join_path
from painter.functions import admin_only

admin_router = Blueprint(
    'admin',
    'admin'
)


@admin_router.route('/admin', methods=('GET',))
@admin_only
def admin() -> str:
    """
    :return: return's admin template
    """
    return render_template('admin/admin.html')
