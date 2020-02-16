$(document).ready(() =>{
    //tooltips
    $('[data-toggle="tooltip"]').tooltip();
    $('#setting-form').submit((e) => {
        e.preventDefault();
    })
    let colors = $('#colors')
    colors.children('option').each(function(idx, elem) {
        console.log(colors);
        $(elem).css('background-color', $(elem).text().toLowerCase());   
        if($(elem).text().toLowerCase() == 'black'){
            $(elem).css('color', 'white');
        }
    });
    $('.custom-range').change(function(e){
        $('.range-text')
            .filter(`span[for="${this.id}-val"]`)
            .text(this.value);
    });
    colors.change(function(e) {
        let option = $(this).siblings('option:selected').first();
        $(this).css('background-color', $(option).text().toLowerCase());   
        if($(option).text().toLowerCase() == 'black'){
            $(option).css('color', 'white');
        }
    });
})
