$(window).on('load', function() {
    $('#expires').datetimepicker({
        format: 'DD/MM/YYYY H:mm', 
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
        }
    })
    $('#ban-form').submit(function(e) {
        e.preventDefault();
        $.post({
            url:this.getAttribute('action'),
            data:$(this).serialize()
        })
        .fail(() => alert('error'))
    });
    $('#submit-ban-form').click(() => {
        $('#ban-from').submit();
    })
})