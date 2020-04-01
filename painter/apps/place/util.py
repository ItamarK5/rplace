from flask import redirect
from werkzeug import Response


def auto_redirect(url: str) -> Response:
    """
    :param url: to redirect the user accessing the page
    :return: 302 Response : Redirect to the page
    """
    # a decoy function
    def view_func():
        return redirect(url)
    if not isinstance(url, str):
        raise TypeError("Url must be string for redirecting")
    # then check if valid
    return view_func
