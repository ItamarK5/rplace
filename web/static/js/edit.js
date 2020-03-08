$(document).ready(function() {
    $('#date-time-picker').datetimepicker({
        format: 'DD/MM/YYYY H:mm', 
        showTodayButton: true, 
        showClear: true,
        showClose: true,
        icons: {
            time: 'fas fa-clock',
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
})