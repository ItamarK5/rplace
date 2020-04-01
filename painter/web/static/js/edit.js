// shortcuts
const history_table = $('#history-table');
// map for note type
const NoteTypeEnums = {
    unbanned_date: {row_class:'primary', text:'Future Unbanned Record'},
    banned_date: {row_class:'warning', text:'Future Banned Record'},
    unbanned: {row_class:'success', text:'Active Record'},
    banned: {row_class:'danger', text:'Banned Record'},
    note : {row_class:'info', text:'Note Record'},
}
const NULL_NOTE = {
    type:'note',
    post_date:'',
    writer:'',
    description:'',  
    can_edit:false
}


// get the user name from the url (that suppose to be)
const GetUserName = () => window.location.pathname.split('/')[2];
const getTargetRow = () => $('tr[targeted="true"]');
// create row note from note data
const MakeNoteRow = (note) => {
    // note attributes needed:
    let note_row_type = NoteTypeEnums[note.type];
    let row = $('<tr></tr>')
                .addClass('table-' + note_row_type.row_class)
                .addClass('note-history-row')
                .attr({
                    'data-item': note.id,
                });
    row.append($('<td></td>').text(note.post_date));
    row.append($('<td></td>').text(note.writer));
    row.append($('<td></td>').text(note_row_type.text));
    return row;
}

// create page button from page data
function makePageButton(num, text=null){
    if(_.isNull(text)){
        text = _.isNull(num) ? 'none' : num.toString() 
    }
    // then
    is_disabled =  _.isNull(num) || isNaN(num);
    let button = $('<button></button>').attr({
        type:'button',
        href: is_disabled ? 'none' : num.toString()
    }).text(text).addClass('btn').addClass('btn-secondary').addClass('page-button');
    if(is_disabled){
        button.addClass('disabled')
    }
    console.log(button)
    return button
}

const focusNoteRow = (note_row) => {
    let row_class = NoteTypeEnums[notes.get_notes_row(note_row).type].row_class
    $(note_row).addClass(`bg-${row_class}`);
    $(note_row).removeClass(`table-${row_class}`);
}

const unfocusNoteRow = (note_row) => {
    let row_class = NoteTypeEnums[notes.get_notes_row(note_row).type].row_class
    $(note_row).addClass(`table-${row_class}`);
    $(note_row).removeClass(`bg-${row_class}`);
}

function displayNoteView(note){
    console.log(Boolean(note), note)
    note = Boolean(note) ? note : {
        type:'note',
        post_date:'',
        writer:'',
        description:'',  
        can_edit:false     
    }
    if(note.type == 'note'){
        $('.record-row:not(.d-none)').addClass('d-none')
    } else {
        $('.record-row.d-none').removeClass('d-none');
    }
    $('#post-date-field').val(note.post_date);
    $('#writer-field').val(note.writer);
    $('#description-field').text(note.description)
    if(note.type != 'note'){
        $('#affect-from-field').val(_.isNull(note.affect_from) ? note.post_date : note.affect_from);    // if the date was from the same time
        $('#active-field').val(note.active);
        $('#reason-field').text(note.reason);
    } else {
        $('#reason-field').text('')
        $('#affect-from-field').text('')
        $('#active-field').text('')
    }
    if(note.can_edit){
        $('#edit-note-tools').removeClass('d-none');
        $('#description-field').prop('disabled', false);
    } else {
        $('#edit-note-tools').addClass('d-none');
        $('#description-field').prop('disabled', true);
    }
    $('#edit-note-button').prop('disabled', true)
}

const notes = {
    pages:null,
    prev_ref:null,
    next_ref:null,
    current_page:null,
    __display_note:null,
    query:null,
    get display_note() {
        return this.__display_note;
    },
    set display_note(value){
        if(value != this.__display_note){
            this.__display_note = value;   
            displayNoteView(value);
        }
    },
    get_notes_row(row_selector) {
        return this.query[
            _.findIndex(
                this.query, 
                (note) => note.id == parseInt($(row_selector).attr('data-item'))
            )
        ];
    },
    update_notes(){
        this.makeHistory()
        this.makePages()
    },
    makeHistory(){
        history_table.children('tr').remove();
        this.query.forEach((value, idx) => {
            history_table.append(MakeNoteRow(value, idx))
        });
        // events
        $('.note-history-row').hover(
            function() {
                focusNoteRow(this)
            },
            function(){
                if($(this).attr('targeted') != 'true'){
                    unfocusNoteRow(this);     
                }
            }
        )
        $('.note-history-row').click(function() {
            let data_item = $(this).attr('data-item');
            $('tr[targeted="true"]').each(function() {
                if(this.attr('data-item') = data_item){
                    $(this).attr('targeted', "true");
                    unfocusNoteRow(this);
                }
            })
            $(this).attr('targeted', "true");
            focusNoteRow(this);
            notes.display_note = notes.get_notes_row(this);
        })
    },
    makePages(){
        let page_group = $('#page-group');
        $('.page-button').remove();
        page_group.append(makePageButton(this.prev_ref, 'Prev'));
        this.pages.forEach((val) => {
            if(_.isNull(val)){
                val = '...'
            }
            let button = makePageButton(val);
            console.log(val, this.current_page)
            if(val == this.current_page){
                button.addClass('active')
            }
            page_group.append(button)
        })
        page_group.append(makePageButton(this.next_ref, 'Next'));
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
                ajaxGetPage(this.getAttribute('href'))
            }
        });
    }
};

function ajaxErrorAlert(err, result_func) {
    let swal = Swal.fire({
        title: 'Error!',
        icon: 'error',
        html: err.responseText
        showCanelButton: _.isFunction(result_func)
    })
    if(result_func){
        swal.then(result_func);
    }
}


function ajaxGetPage(page=1){
    return $.get({
        url:'/get-notes',
        data: {name:GetUserName(), page:parseInt(page)},       
        contentType: 'application/json;charset=UTF-8',
        success: (data) => {
            notes.pages=data.pages;
            notes.query=data.query;
            notes.prev_ref=data.prev_ref;
            notes.next_ref=data.next_ref;
            notes.current_page=data.current_page;
            notes.update_notes()
        },
        error:ajaxErrorAlert
    }).catch(error => {
        ajaxErrorAlert({responseText:'fail-to-get-message'})
    });
}

$.fn.serializeForm = function() {
    var output = {csrf_token:csrf_token};
    var fields_array = this.serializeArray();
    $.each(fields_array, function() {
        if (output[this.name]) {
            if (!output[this.name].push) {
                output[this.name] = [output[this.name]];
            }
            output[this.name].push(this.value || '');
        } else {
            output[this.name] = this.value || '';
        }
    });
    return output;
};

$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip()
    $('#historyModal').on('show.bs.modal', (e) => {
        if(notes.current_page == null){
            e.stopPropagation();
            Swal.fire({
                icon:'warning',
                title:'Didnt gain history',
                text:'Cant load notes history from server, pless wait until it loads'
            })
    
        }
    })
    ajaxGetPage();
    $('#ban-form').submit(function(e) {
        let success_message = $('#ban-form .success-message')[0];
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        $('.error-list').children().remove();
        e.preventDefault();
        let args = $(this).serializeForm();
        $.ajax({
            url:$(this).attr('action'),
            method:'POST',
            data:JSON.stringify(args),
            contentType: "application/json;charset=utf-8",
            success: (data) => {
                console.log(data, typeof(data))
               if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
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
            error:ajaxErrorAlert
        });
    });
    $('#note-form').submit(function(e) {
        let success_message = $('#note-form .success-message')[0];
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        let args = $(this).serializeForm();
        $('#note-form .error-list').children().remove();
        e.preventDefault();
        console.log(args)
        $.post({
            url:$(this).attr('action'),
            data:JSON.stringify(args),
            contentType: "application/json;charset=utf-8",
            success: (data) => {
                if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
                    // need to work for csrf error
                    _.pairs(data.errors).forEach(function(row){
                        let field = row[0];
                        row[1].forEach(function(err){
                            $('<ul></ul>')
                            .text(err)
                            .addClass("center-text list-group-item list-group-item-danger")
                            .appendTo($(`#note-form .error-list[error-for="${field}"]`).first())
                        })
                    })
                }
            }
        }).fail(ajaxErrorAlert);
    });
    $('#submit-ban-form').click(() => {
        $('#ban-form').submit();
    });
    $('#submit-note-form').click(() => {
        $('#note-form').submit();
    })
    $('#set-affect-from').click(function() {
        let field = $('#affect_from')[0];
        if (this.checked) {
            field.removeAttribute('disabled');
        } else {
            field.setAttribute('disabled', 'disabled')
        }
    })
    $('#affect_from').attr('disabled', 'disabled');
    $('#rank-button').click(function() {
        let name = this.getAttribute('enum-name');
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
                    error: ajaxErrorAlert
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
        ajaxGetPage(notes.current_page).then(() => {
            $('#refresh-history').children('div').remove();
            $('#refresh-history').text('refresh');
        })
    });
    $('#remove-note-button').click(() => {
        let targeted_row = getTargetRow();
        if(targeted_row){
            $.post({
                url:`/delete-note`,
                data:{idx:targeted_row.attr('data-item').toString()},
                success: (response) => {
                    if(response.success){
                        Swal.alert({
                            icon:'success',
                            text:'Success',
                            error:'The Note was removed'
                        })
                    }
                    note.display_note = null;
                    targeted_row.remove()
                },
                error: ajaxErrorAlert
            })
        }
    })
    $('#description-field').on('input', function(e) {
        console.log(notes.display_note)
        if(notes.display_note){
            $('#edit-note-button').prop('disabled', $(this).val() == notes.display_note.description)
        }
    })
    $('edit-note-button').click(() => {
        if(notes.current_display.can_edit){
            $.ajax({
                
            })
        }
    })

})

/** serialize the date input */
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