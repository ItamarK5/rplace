from flask import Blueprint, render_template, Response
from os.path import join as path_join
from painter.constants import WEB_FOLDER
from flask_login import login_required
<<<<<<< HEAD
=======

>>>>>>> parent of 9614fde... 2.4.3
place_router = Blueprint('place', 'place',
                         static_folder=path_join(WEB_FOLDER, 'static'),
                         template_folder=path_join(WEB_FOLDER, 'templates'))


@place_router.route('/place', methods=('GET',))
@login_required
def place():
    return render_template('place.html')
<<<<<<< HEAD


@place_router.route('/', methods=('GET',))
@login_required
def home() -> Response:
    """
    :return: return the home page
    """
    return render_template('home.html')

=======
>>>>>>> parent of 9614fde... 2.4.3
