const history_table = $('#history-table');
const NoteTypeEnums = {
    unbanned_date: {row_class:'primary', text:'Future Unbanned Record'},
    banned_date: {row_class:'warning', text:'Future Banned Record'},
    unbanned: {row_class:'success', text:'Active Record'},
    banned: {row_class:'danger', text:'Banned Record'},
    note : {row_class:'info', text:'Note Record'},
    /**
     * 
     * @param {Note object} note 
     */

}

const GetUserName = () => window.location.pathname.split('/')[2];

const MakeNoteRow = (note) => {
    console.log(note)
    // note attributes needed:
    let note_row_type = NoteTypeEnums[note.type];
    console.log(note_row_type)
    let row = $('<tr></tr>').addClass('table-' + note_row_type.row_class).addClass('note-history-row').attr('note-type', note.type);
    row.append($('<td></td>').text(note.post_date));
    row.append($('<td></td>').text(note.writer));
    row.append($('<td></td>').text(note_row_type.text));
    return row;
}

function pageButton(num, text=null){
    if(text == null){
        text = num.toString()
    }
    // then
    let button = $('<button></button>').attr({
        type:'button',
        href: num
    }).text(text).addClass('btn').addClass('btn-secondary').addClass('page-button');
    if(_.isNull(num)){
        button.addClass('disabled')
    }
    return button
}

const focusNoteRow = (page_button) => {
    let row_class = NoteTypeEnums[$(page_button).attr('note-type')].row_class
    $(page_button).addClass(`bg-${row_class}`);
    $(page_button).removeClass(`table-${row_class}`);
}

const unfocusNoteRow = (page_button) => {
    let row_class = NoteTypeEnums[$(page_button).attr('note-type')].row_class
    $(page_button).addClass(`table-${row_class}`);
    $(page_button).removeClass(`bg-${row_class}`);
}

const notes = {
    pages:null,
    prev_ref:null,
    next_ref:null,
    current_page:null,
    query:null,
    update_notes(){
        this.makeHistory()
        this.makePages()
    },
    makeHistory(){
        history_table.children('tr').remove();
        this.query.forEach((value) => {
            history_table.append(MakeNoteRow(value))
        });
        $('.note-history-row').hover(
            function() {
                focusNoteRow(this)
            },
            function(){
                if(!this.hasAttribute('is-selected')){
                    unfocusNoteRow(this);                                    
                }
            }
        )
        $('.note-history-row').click(function() {
            let sibling = $(this).siblings('tr[is-selected="1"]')[0];
            if(sibling){
                sibling.removeAttribute('is-selected');
                unfocusNoteRow(sibling);
            }
            $(this).attr('is-selected', '1');
            focusNoteRow(this);
        })
    },
    makePages(){
        let page_group = $('#page-group');
        page_group.children().remove();
        page_group.append(pageButton(this.prev_ref, 'Prev'));
        this.pages.forEach((val) => {
            let button = pageButton(val);
            console.log(val, this.current_page)
            if(val == this.current_page){
                button.addClass('active')
            }
            page_group.append(button)
        })
        page_group.append(pageButton(this.next_ref, 'Next'));
        $('.page-button').click(function(e) {
            if($(this).hasClass('disabled')){
                e.preventDefault();
                Swal.fire({
                    icon:'error',
                    title:'Cannot access page'
                })
            } else if($(this).hasClass('active')){
                e.preventDefault()
            } else {
                ajax_get_page(this.getAttribute('href'))
            }
        });
    }
};

function ajax_error_alert(err) {
    Swal.fire({
        title: 'Error!',
        icon: 'error',
        html: err.responseText
    })
}


function ajax_get_page(page=1){
    return $.ajax({
        url:'/get-notes',
        method:'GET',
        data: {name:GetUserName(), page:parseInt(page)},
        contentType: 'application/json;charset=UTF-8',
        success: (data) => {
            notes.pages=data.pages;
            notes.query=data.query;
            notes.prev_ref=data.prev_ref;
            notes.next_ref=data.next_ref;
            notes.current_page=data.current_page;
            notes.update_notes()
        }
    })
}

const sock = io('/edit-profile');

sock.on('connect', () => {
    url_recipe = window.location.pathname.split('/')
    sock.emit('join', url_recipe[url_recipe.length-1])
})

sock.on('reconnect', () => {
    url_recipe = window.location.pathname.split('/')
    sock.emit('join', url_recipe[url_recipe.length-1])
});


function FormArgs(selector){
    let arr = _.map(
        selector.serialize().split('&'), 
        (field) => field.split('=')
    )
    arr.push(['csrf_token', csrf_token])
	return _.object(arr);
}

$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip()
    $('#historyModal').on('show.bs.modal', (e) => {
        console.log()
        if(notes.current_page == null){
            e.stopPropagation();
            Swal.fire({
                icon:'warning',
                title:'Didnt gain history',
                text:'Cant load notes history from server, pless wait until it loads'
            })
    
        }
    })
    ajax_get_page();
    $('#ban-form').submit(function(e) {
        let success_message = $('#ban-form .success-message')[0];
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        $('.error-list').children().remove();
        e.preventDefault();
        let args = FormArgs($('#ban-form'))
        $.ajax({
            url:$(this).attr('action'),
            method:'POST',
            data:args,
            success: (data) => {
                if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
                    let fields = data.errors;
                    // need to work for csrf error
                    _.pairs(data.errors).forEach(function(row){
                        let field = row[0];
                        let errors = row[1];
                        console.log(field, errors);
                        errors.forEach(function(err){
                            $('<ul></ul>')
                            .text(err)
                            .addClass("center-text list-group-item list-group-item-danger")
                            .appendTo($(`#ban-form .error-list[error-for="${field}"]`).first())
                        })
                    })
                }
            },
            error:ajax_error_alert
        });
    });
    $('#note-form').submit(function(e) {
        let success_message = $('#note-form .success-message')[0];
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        let args = FormArgs($(this));
        $('#note-form .error-list').children().remove();
        e.preventDefault();
        $.ajax({
            url:$(this).attr('action'),
            method:'POST',
            data:args,
            success: (data) => {
                if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
                    let fields = data.errors;
                    // need to work for csrf error
                    _.pairs(data.errors).forEach(function(row){
                        let field = row[0];
                        let errors = row[1];
                        console.log(field, errors);
                        errors.forEach(function(err){
                            $('<ul></ul>')
                            .text(err)
                            .addClass("center-text list-group-item list-group-item-danger")
                            .appendTo($(`#note-form .error-list[error-for="${field}"]`).first())
                        })
                    })
                }
            },
            error:ajax_error_alert
        });
    });
    $('#submit-ban-form').click(() => {
        $('#ban-form').submit();
    });
    $('#submit-note-form').click(() => {
        $('#note-form').submit();
    })
    $('#set-affect-from').click(function() {
        let field = $('#affect_from')[0];
        console.log(this, this.checked)
        if (this.checked) {
            field.removeAttribute('disabled');
        } else {
            field.setAttribute('disabled', 'disabled')
        }
    })
    $('#affect_from').attr('disabled', 'disabled');
    $('#rank-button').click(function() {
        let name = this.getAttribute('enum-name');
        console.log(name, 5)
        Swal.fire({
            title: 'Are you sure?',
            text: `You want to set this user's rank to ${name}`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes Set Rank!'
        }).then((result) => {
            if (result.value) {
                console.log(name)
                $.ajax({
                    url: `/set-user-role/${GetUserName()}`,
                    method: 'POST',
                    contentType: 'application/json;charset=UTF-8',
                    data: name,
                    // success message
                    success: function(data) {
                        Swal.fire({
                            title: data.success ? 'Role Changed' : 'Error!',
                            icon: data.success ? 'success' : 'error',
                            text: data.text
                        });
                    },
                    // error message
                    error: ajax_error_alert
                })
            }
        })
    });
    $('#refresh-history').click(function(){
        $(this).text('')
        $(this).append(
            $('<div></div>')
            .addClass('text-secondary spinner-border')
            .append($('<span></span>')
            .addClass('sr-only')
            .text('Loading'))
        )
        ajax_get_page(notes.current_page).then(() => {
            $('#refresh-history').children('div').remove();
            $('#refresh-history').text('refresh');
        })
    });
})

$(window).on('load', function() {
    $('#affect_from').datetimepicker({
        format: 'DD/MM/YYYY HH:mm',
        showTodayButton: true,
        showClear: true,
        showClose: true,
        icons: {
            time: 'far fa-clock',
            date: 'fas fa-calendar',
            up: 'fas fa-arrow-up',
            down: 'fas fa-arrow-down',
            previous: 'fas fa-chevron-left',
            next: 'fas fa-chevron-right',
            today: 'fas fa-calendar-check-o',
            clear: 'fas fa-trash',
			close: 'fas fa-times'
		},
        timeZone: 'utc-0'
    })
    
});