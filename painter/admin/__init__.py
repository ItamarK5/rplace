from flask_admin import Admin
from .views import user_view

admin = Admin(
    name='Social Painter Admin',
)

admin.add_view(views.user_view)

