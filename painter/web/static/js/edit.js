const history_table = $('#history-table');
const NoteTypeEnums = {
    unbanned_date: {row_class:'bg-success', text:'Future Unbanned Record'},
    banned_date: {row_class:'table-warning', text:'Future Banned Record'},
    unbanned: {row_class:'table-success', text:'Active Record'},
    banned: {row_class:'table-danger', text:'Banned Record'},
    note : {row_class:'note', text:'Note Record'},
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
    let row = $('<tr></tr>').addClass(note_row_type.row_class);
    row.append($('<td></td>').text(note.post_date));
    row.append($('<td></td>').text(note.writer));
    row.append($('<td></td>').text(note_row_type.text))
    return row;
}

const notes = {
    pages:null,
    pref_ref:null,
    next_ref:null,
    query:null,
    update_notes(){
        console.log(this)
        history_table.children('tr').remove();
        this.query.forEach((value) => {
            console.log(value)
            history_table.append(MakeNoteRow(value))
        })
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
    $.ajax({
        url:'/get-notes',
        method:'GET',
        data: {name:GetUserName(), page:parseInt(page)},
        contentType: 'application/json;charset=UTF-8',
        success: (data) => {
            console.log(data)
            notes.pages=data.pages;
            notes.query=data.query;
            notes.prev_ref=data.prev_ref;
            notes.next_ref=data.next_ref;
            notes.update_notes()
        }
    })
}

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

const sock = io('/edit-profile');
sock.on('connect', () => {
    url_recipe = window.location.pathname.split('/')
    sock.emit('join', url_recipe[url_recipe.length-1])
})
sock.on('reconnect', () => {
    url_recipe = window.location.pathname.split('/')
    sock.emit('join', url_recipe[url_recipe.length-1])
});

 /*
    $('#setting-form').submit((e) => {
        e.preventDefault();
        let form = $('#setting-form');
        $.ajax({
            url:form.attr('action'),
            type:form.attr('method'),
            data:form.serialize(),
            success: (data) => {
                $('.info-div').addClass('d-none');
                console.log(data);
                if(data.valid){
                    $('#success-form').text('values have changed').removeClass('d-none');
                } else {
                    data.errors.forEach((val) => {
                        let ele = $(`.errors-list[for="${val[0]}"]`);
                        val[1].forEach((err) => {
                            $('<span>').text(err).appendTo(ele[0]);
                        });
                    });
                    data.values.forEach((val) => {
                        $(`#${val[0]}`).val(val[1].toString()).change();
                    });
                }
            }
        })
    });
    $('.range-text').each((idx, ele) => {
        let inp = $(`#${ele.getAttribute('for')}`);
        console.log(inp, ele);
        $(ele).text(inp.val());
    });
    let colors = $('#colors')
    colors.children('option').each(function(idx, elem) {
        $(elem).css({
            'background-color':$(elem).text().toLowerCase(),
            color: $(elem).text().toLowerCase() == 'black' ? 'white' : 'black'
        });   
    });
    $('.custom-range').change(function(e){
        $('.range-text')
            .filter(`span[for="${this.id}"]`)
            .text(this.value);
    });
    colors.change(function(e) {
        let option = $(this).children('option:selected');
        $(this).css({
            'background-color':$(option).text().toLowerCase(),
            color: $(option).text().toLowerCase() == 'black' ? 'white' : 'black'
        });
    })
    */