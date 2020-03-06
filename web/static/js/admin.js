$(document).ready(() => {
    $('[data-toggle="tooltip"]').tooltip();
    $('tr').click(function() {
        let name = $(this).children('.name-col').text();
        if(name){
            window.location.href = `/edit/${$(this).children('.name-col').text()}`
        };
    });
    $('#place-button').click(function(){
        $.get(
            '/admin-power-button',
            $(this).attr('state')
        )
    })
});
