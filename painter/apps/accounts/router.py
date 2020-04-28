"""
router
contains the paths of the application related to login or quiting
"""
from flask import Blueprint

accounts_router = Blueprint('auth', __name__)
