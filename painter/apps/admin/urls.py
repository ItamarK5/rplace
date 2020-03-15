from datetime import datetime

from flask import Blueprint, render_template, abort, request, url_for, redirect, jsonify, escape
from flask.wrappers import Response
from flask_login import current_user
from werkzeug.exceptions import BadRequest

from painter.extensions import datastore
from painter.models.notes import Record, Note
from painter.models.user import User
from painter.models.user import reNAME
from .forms import RecordForm, NoteForm
from .utils import only_if_superior, admin_only
from ..profile_form import PreferencesForm

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
    response.headers["Pragma"] = "no-store"
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
    page = request.args.get('page', '1')
    if not page.isdigit():
        abort(400, 'Given page isn\'t a number', description='Are you mocking this program? you'
                                                             ' an admin tries to edit the url')
    page = int(page)
    if not (1 <= page <= pagination.pages):
        abort(404, 'Page index Not Found')
    return render_template('accounts/admin.html', pagination=pagination)


@admin_router.route('/edit/<string:name>', methods=('GET',))
@admin_only
def edit_user(name: str) -> Response:
    """
    :param: name of user
    :returns: the web-page to edit the matched user (to the name) data
    """
    if reNAME.match(name) is None:
        abort(400, 'Name isn\'t good')
    user = User.query.filter_by(username=name).first_or_404()
    if user == current_user:
        return redirect(url_for('place.profile'))
    if not current_user.is_superior_to(user):
        # forbidden error
        abort(403, f"You are not allowed to edit the user {user.username}")
    preference_form = PreferencesForm()
    ban_form = RecordForm(set_banned=user.is_active())
    note_form = NoteForm()
    return render_template(
        'accounts/edit.html',
        user=user,
        form=preference_form,
        ban_form=ban_form,
        note_form=note_form
    )


@admin_router.route('/edit-preferences-submit/<string:name>', methods=("POST",))
@only_if_superior
def profile_ajax():
    form = PreferencesForm()
    # detecting for user
    if form.validate_on_submit():
        key, val = form.safe_first_hidden_fields()
        if key == 'url':
            current_user.url = val if val != '' and val is not None else None
        elif key == 'x':
            current_user.x = val
        elif key == 'y':
            current_user.y = val
        elif key == 'scale':
            current_user.scale = val
        elif key == 'color':
            current_user.color = val
        else:
            key = None
        if key is not None:
            datastore.session.add(current_user)
            datastore.session.commit()
            # https://stackoverflow.com/a/26080784
            return jsonify({'success': True, 'id': key, 'val': val})
        else:
            return jsonify({
                'success': False,
                'errors': ['Not valid parameter {}'.format(key)]
            })
    return jsonify({
        'success': False,
        'errors': next(iter(form.errors.values()))
    })
    # else


@admin_router.route('/ban-user/<string:name>', methods=('POST',))
@only_if_superior
def change_ban_status(user: User) -> Response:
    """
    :param user: the user that I add the record
    :return: nothing
    adds a ban record for the user
    """
    form = RecordForm()
    # check a moment for time
    if form.validate_on_submit():
        record = Record(
                active=not form.set_banned.data,
                expire=form.expires.data,
                reason=escape(form.reason.data),
            )
        datastore.session.add(record)
        datastore.session.commit()
        datastore.session.add(Note(
            user=user.id,
            description=escape(form.note.data),
            declared=datetime.now(),
            writer=current_user.id,
            ban_record=record.id
        ))
        datastore.session.commit()
        user.forget_is_active()
        return jsonify({'valid': True})
    # else
    else:
        print(form.errors)
        return jsonify({
            'valid': False,
            'errors': dict(
                [(field.name, field.errors) for field in form if field.id != 'csrf_token']
            )
        })


@admin_router.route('/add-note/<string:name>', methods=('POST',))
@only_if_superior
def add_note(user: User) -> Response:
    """
    :param user: the user that I add the record
    :return: nothing
    adds a ban record for the user
    """
    form = NoteForm()
    # check a moment for time
    if form.validate_on_submit():
        note = Note(

        )
        datastore.session.add(Note(
            user=user.d,
            writer=current_user.id,
            declared=datetime.now(),
            description=escape(form.description),
            ban_Record=None
        ))
        datastore.session.commit()
        user.forget_is_active()
        return jsonify({'valid': True})
    # else
    else:
        print(form.errors)
        return jsonify({
            'valid': False,
            'errors': dict(
                [(field.name, field.errors) for field in form if field.id != 'csrf_token']
            )
        })
