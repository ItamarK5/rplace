$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip();
    $('tr').click(function() {
        window.location.href = `/edit/${$(this).children('.name-col').text()}`
    });
});
