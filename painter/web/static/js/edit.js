const formRows = (selector) => $(selector).children('.form-row');

function ajax_error_alert(err) {
    Swal.fire({
        title: 'Error!',
        icon: 'error',
        html: err.responseText
    })
}
$(document).ready(() => {
    $('#ban-form').submit(function(e) {
        let success_message = $('#ban-form > .success-message')[0];
        let rows = formRows(this);
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        $('.error-list').children().remove();
        e.preventDefault();
        $.ajax({
            method: "POST",
            url: this.getAttribute('action'),
            data: $(this).serialize(),
            success: (data) => {
                if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
                    let errors = data.errors;
                    if (errors.expires) {
                        errors.expires.forEach((val) => {
                            $('<ul></ul>')
                                .addClass("center-text list-group-item list-group-item-danger")
                                .text(val)
                                .appendTo(rows.children('.error-list[error-for="expires"]').first())
                        })
                    }
                    if (errors.reason) {
                        errors.reason.forEach((val) => {
                            $('<ul></ul>')
                                .addClass("center-text list-group-item list-group-item-danger")
                                .text(val)
                                .appendTo(rows.children('.error-list[error-for="reason"]').first())
                        })
                    }
                    if (errors.note) {
                        errors.note.forEach((val) => {
                            $('<ul></ul>')
                                .addClass("center-text list-group-item list-group-item-danger")
                                .text(val)
                                .appendTo(rows.children('.error-list[error-for="note"]').first())
                        })
                    }
                }
            },
            error: ajax_error_alert
        })
    });
    $('#note-form').submit(function(e) {
        let success_message = formRows('#note-form').children('.success-message')[0];
        if (!success_message.hasAttribute('hidden')) {
            success_message.toggleAttribute('hidden');
        }
        let rows = formRows(this);
        $(this).children('.error-list').children().remove();
        e.preventDefault();
        $.ajax({
            method: "POST",
            url: this.getAttribute('action'),
            data: $(this).serialize(),
            success: (data) => {
                if (data.valid) {
                    success_message.removeAttribute('hidden')
                } else {
                    let errors = data.errors;
                    if (errors.description) {
                        errors.description.forEach((val) => {
                            $('<ul></ul>')
                                .addClass("center-text list-group-item list-group-item-danger")
                                .text(val)
                                .appendTo(rows.children('.error-list[error-for="note"]').first())
                        })
                    }
                }
            },
            error: ajax_error_alert
        })
    });
    $('#submit-ban-form').click(() => {
        $('#ban-form').submit();
    });
    $('#submit-note-form').click(() => {
        $('#note-form').submit();
    })
    $('#set-expire').click(function() {
        let field = $('#expires')[0];
        console.log(this, this.checked)
        if (this.checked) {
            field.removeAttribute('disabled');
        } else {
            field.setAttribute('disabled', 'disabled')
        }
    })
    $('#expires').attr('disabled', 'disabled');
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
                    url: `/set-user-role/${window.location.pathname.split('/')[2]}`,
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
    $('#expires').datetimepicker({
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
    
})