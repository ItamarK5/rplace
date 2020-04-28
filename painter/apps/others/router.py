"""
router for other staff
contains paths for the meme response pages and
static pages
"""
from flask import Blueprint

other_router = Blueprint(
    'other',
    'other',
    static_folder='/web',
)
