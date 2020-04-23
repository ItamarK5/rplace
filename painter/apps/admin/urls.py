from datetime import datetime

from flask import render_template, abort, request, url_for, redirect, jsonify
from flask.wrappers import Response
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug import exceptions

from painter.backends import lock
from painter.backends.extensions import datastore
from painter.backends.skio import ADMIN_NAMESPACE, PAINT_NAMESPACE, sio
from painter.models import Record, Note, Role, User
from painter.others.wtforms_mixins import UsernamePattern

from . import admin_router
from .forms import RecordForm, NoteForm
from .utils import only_if_superior, admin_only, superuser_only, json_response, validate_get_notes_param
from painter.others.wtforms_mixins import UsernamePattern


@admin_router.route('/admin', methods=('GET',))
@admin_only
def admin() -> Response:
    """
    :return: return's admin template
    """
    # pagination
    pagination = User.query.paginate(
        per_page=5,
        max_per_page=5
    )
    # try get page
    return render_template('profiles/admin.html', pagination=pagination)


@admin_router.route('/add-record', methods=('POST',))
@only_if_superior
def add_record(user: User) -> Response:
    """
    :param user: the user to add the record
    :return: json response with the errors on adding the record/success message
    """
    form = RecordForm()
    if form.validate_on_submit():
        # create record
        record = Record(
            user_subject_id=user.id,
            description=form.note_description.data,
            user_writer_id=current_user.id,
            active=not form.set_banned.data,
            affect_from=form.affect_from.data,
            reason=form.reason.data
        )
        datastore.session.add(record)
        datastore.session.commit()
        user.forget_last_record()
        return jsonify(valid=True)
    # csrf token has its own action
    elif form.csrf_token.errors:
        abort(CSRFError)
    # else:
    return jsonify(
        valid=False,
        errors=dict([(field.name, field.errors) for field in iter(form) if field.id != 'csrf_token'])
    )


@admin_router.route('/add-note/<string:name>', methods=('POST',))
@only_if_superior
def add_note(user: User) -> Response:
    """
    :param user: the user to add the record to
    :return: JSON response
    adds a note to the user
    """
    form = NoteForm()
    # check a moment for time
    if form.validate_on_submit():
        note = Note(
            user_subject_id=user.id,
            user_writer_id=current_user.id,
            post_date=datetime.now(),
            description=form.description.data,
        )
        datastore.session.add(note)
        datastore.session.commit()
        # forget last record for refinding
        user.forget_last_record()
        return jsonify({'valid': True})
    # else
    return jsonify(
        valid=False,
        errors=dict([(field.name, field.errors) for field in iter(form) if field.id != 'csrf_token'])
    )


@admin_router.route('/change-lock-state', methods=('POST',))
@superuser_only
def set_admin_button() -> Response:
    """
    :return: json response
    """
    if request.data not in (b'1', b'0'):
        return json_response(False, 'Unknown data')
    new_state = request.data == b'0'
    # else switch state
    lock.set_switch(new_state)
    # emit changes
    sio.emit('change-lock-state', new_state, namespace=PAINT_NAMESPACE)
    sio.emit('set-lock-state', new_state, namespace=ADMIN_NAMESPACE, include_self=False)
    return json_response(True, new_state)


@admin_router.route('/edit/<string:name>', methods=('GET',))
@admin_only
def edit_user(name: str) -> Response:
    """
    :param: name of user
    :returns: the web-page to edit the matched user (to the name) data
    """
    if UsernamePattern.match(name) is None:
        abort(exceptions.BadRequest.code, 'Name isn\'t good')
    # get page of edit user
    user = User.query.filter_by(username=name).first_or_404()
    if user == current_user:
        return redirect(url_for('place.profile'))
    # allow only for superior users
    if not current_user.is_superior_to(user):
        # forbidden error
        abort(exceptions.Forbidden.code, f"You are not allowed to edit the user {user.username}")
    # create new record form/note_form for submitting new ones
    record_form = RecordForm(set_banned=user.is_active)
    note_form = NoteForm()
    return render_template(
        'profiles/edit.html',
        user=user,
        record_form=record_form,
        note_form=note_form,
        Role=Role
    )


@admin_router.route('/get-active-state', methods=('GET',))
@admin_only
def get_active_state() -> Response:
    """
    :return: json response
    get active state of the board, only for admins
    """
    try:
        return jsonify(lock.is_open())
    except:
        return jsonify(None)


@admin_router.route('/set-user-role/<string:name>', methods=('POST',))
@only_if_superior
def set_role(user: User) -> Response:
    """
    :param user: the user
    :return: JSON response of the error data or success
    sets the role o the user by the given value, if not return error
    """
    if not current_user.has_required_status(Role.superuser):
        abort(exceptions.Forbidden.code)  # forbidden
    # get value
    if request.data == b'Admin':
        new_role = Role.admin
    elif request.data == b'Common':
        new_role = Role.common
    else:
        return json_response(False, 'Unknown value')
    # if the passed role is the role the user is in
    if new_role == user.role:
        return json_response(False, 'Refresh the page to pick different role')
    # else
    user.role = new_role
    # save data
    datastore.session.add(user)
    datastore.session.commit()
    return json_response(True, 'Pless refresh the page to see changes')


@admin_router.route('/get-notes', methods=('GET',))
@only_if_superior
def get_user_notes(user: User):
    """

    :param user:
    :return: JSON response contaiing:
    query: group of notes
    prev_ref: previous page to the asked one
    next_ref: next page to the to the asked one displayed
    pages: the pages displayed
    current_page: the current page
    """
    page = validate_get_notes_param('page')
    # get notes for page
    pagination = user.related_notes.paginate(page=page, max_per_page=5)
    return jsonify(
        query=[item.json_format(current_user) for item in pagination.items],
        next_ref=pagination.next_num,
        prev_ref=pagination.prev_num,
        pages=tuple(pagination.iter_pages()),
        current_page=pagination.page
    )


@admin_router.route('/delete-note', methods=('POST',))
def remove_user_note() -> Response:
    """
    :return: json response
    deletes a note about the user
    """
    # in case of fail aborts json error
    try:
        note_index = request.get_json()
        if not isinstance(note_index, int):
            raise TypeError()
    except (exceptions.BadRequest, ValueError, TypeError, KeyError):
        abort(exceptions.BadRequest.code, 'Not valid data')
    # else
    note = Note.query.get_or_404(note_index, description="Note Was Removed")
    # clears the key
    user_last_record = note.user_subject.get_last_record()
    if user_last_record is None or user_last_record.equals(note):
        note.user_subject.forget_last_record()
    try:
        datastore.session.delete(note)
        datastore.session.commit()
    # it must have been removed
    except NoResultFound:
        abort(401, description="Note Was Removed")
    return jsonify({'status': 200, 'response': 'Note Removed Successfully'})


@admin_router.route('/change-note-description', methods=('POST',))
def change_note_description() -> Response:
    """
    :return: JSON response
    changes a note description
    """
    note_index = None
    description = None
    try:
        data = request.get_json()
        note_index = data['id']
        description = data['description']
        # checking for type
        if not (isinstance(description, str) or isinstance(note_index, int)):
            raise TypeError()
    except (exceptions.BadRequest, ValueError, TypeError, KeyError) as e:
        print(e)
        abort(exceptions.BadRequest.code, 'Not valid data')
    if len(description) > 512:
        abort(exceptions.BadRequest.code, 'Note/Record\'s description cannot be more'
                                          ' then 512, you passed {0}'.format(len(description)))
    # else
    note = Note.query.get_or_404(note_index, description="Note Was Removed")
    # handle updates
    note.description = description
    try:
        datastore.session.add(note)
        datastore.session.commit()
    # NoResult => object removed
    except NoResultFound:
        abort(404, description='Note was removed')
    return jsonify({'status': 200, 'response': 'Note Removed Successfully'})
