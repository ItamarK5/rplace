$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip();
    $('td').click(function() {
        window.location.href = `/edit/${
            $(this)
            .siblings('.name-col')
            .text()}`;
    });
});
