from datetime import datetime
from typing import Dict
from flask import Blueprint, render_template, abort, request, url_for, redirect, jsonify, escape
from flask.wrappers import Response
from flask_login import current_user

from painter.backends import lock
from painter.backends.extensions import datastore
from painter.models.notes import Record, Note
from painter.models.role import Role
from painter.models.user import User
from painter.models.user import reNAME
from painter.others.profile_form import PreferencesForm
from .forms import RecordForm, NoteForm
from .utils import only_if_superior, admin_only, superuser_only, json_response, validate_get_notes_param


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
    pagination = User.query.paginate(per_page=10, max_per_page=20)
    # try get page
    page = request.args.get('page', '1')
    if not page.isdigit():
        abort(400, 'Given page isn\'t a number', description='Are you mocking this program? you'
                                                             ' an admin tries to edit the url')
    page = int(page)
    print(pagination.pages)
    if not (1 <= page <= pagination.pages):
        print(1)
        return redirect(url_for('/admin', args={'page': '1'}))
    return render_template('accounts/admin.html', pagination=pagination, lock=lock.is_enabled())


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
    ban_form = RecordForm(set_banned=user.is_active)
    note_form = NoteForm()
    return render_template(
        'accounts/edit.html',
        user=user,
        form=preference_form,
        ban_form=ban_form,
        note_form=note_form,
        Role=Role
    )


@admin_router.route('/edit-preferences-submit/<string:name>', methods=("POST",))
@only_if_superior
def profile_ajax(user: User) -> Response:
    form = PreferencesForm()
    # detecting for user
    if form.validate_on_submit():
        key, val = form.safe_first_hidden_fields()
        if key == 'url':
            user.url = val if val != '' and val is not None else None
        elif key == 'x':
            user.x = val
        elif key == 'y':
            user.y = val
        elif key == 'scale':
            user.scale = val
        elif key == 'color':
            user.color = val
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
            user_subject_id=user.id,
            description=escape(form.note.data),
            post_date=datetime.now(),
            user_writer_id=current_user.id,
            active=not form.set_banned.data,
            affect_from=form.affect_from.data,
            reason=escape(form.reason.data)
        )
        datastore.session.add(record)
        datastore.session.commit()
        user.forget_last_record()
        return jsonify({'valid': True})
    # else
    else:
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
        datastore.session.add(Note(
            user_subject_id=user.id,
            user_writer_id=current_user.id,
            declared=datetime.now(),
            description=escape(form.description.data),
        ))
        datastore.session.commit()
        user.forget_last_record()
        return jsonify({'valid': True})
    # else
    else:
        return jsonify({
            'valid': False,
            'errors': dict(
                [(field.name, field.errors) for field in form if field.id != 'csrf_token']
            )
        })


@admin_router.route('/set-power-button', methods=('POST',))
@superuser_only
def set_admin_button():
    if not current_user.has_required_status(Role.superuser):
        abort(403)  # forbidden
    # else
    if request.data != b'1' and request.data != b'0':
        return json_response(False, 'Unknown data')
    # else
    is_game_paused = request.data == b'0'
    if is_game_paused:
        lock.enable()
        PAINT_NAMESPACE.play_place()
    else:
        lock.disable()
        PAINT_NAMESPACE.pause_place()
    return json_response(True, '1' if is_game_paused else '0')


@admin_router.route('/set-user-role/<string:name>', methods=('POST',))
@only_if_superior
def set_role(user: User) -> Response:
    if not current_user.has_required_status(Role.superuser):
        abort(404)  # forbidden
    # get value
    if request.data == b'Admin':
        new_role = Role.admin
    elif request.data == b'Common':
        new_role = Role.common
    else:
        return json_response(False, 'Unknown value')
    if new_role == user.role:
        return json_response(False, 'Refresh the page to pick different role')
    # else
    user.role = new_role
    datastore.session.add(user)
    datastore.session.commit()
    return json_response(True, 'Pless refresh the page to see changes')


@admin_router.route('/get-notes', methods=('GET',))
@only_if_superior
def get_user_notes(user: User):
    # max_per_page = validate_get_notes_param('max-per-page')
    page = validate_get_notes_param('page')
    # get note number x
    pagination = user.related_notes.paginate(page=page)
    print(pagination.items)
    return jsonify(
        query=[item.json_format() for item in pagination.items],
        next_ref=pagination.next_num,
        prev_ref=pagination.prev_num,
        pages=tuple(pagination.iter_pages())
    )


@admin_router.route('/add-record', methods=('POST',))
@only_if_superior
def add_record(user: User, message: Dict[str, str]):
    form = RecordForm()
    if form.validate_on_submit():
        record = Record(
            user=user.id,
            description=escape(form.note.data),
            declared=datetime.now(),
            writer=current_user.id,
            active=not form.set_banned.data,
            affect_from=form.affect_from.data,
            reason=escape(form.reason.data)
        )
        datastore.session.add(record)
        datastore.session.commit()
        user.forget_last_record()
        return {'valid': True}
    # else
    else:
        return {
            'valid': False,
            'errors': dict(
                [(field.name, field.errors) for field in form]
            )
        }

"""
    1) Get Notes
    2) Delete Note
    3) Remove Note
    4) Admin Only - Remove Note
    5) Superuser Only - Remove
"""
