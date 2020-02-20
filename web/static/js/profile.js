const colors = [
    'white', 'black', 'gray', 'silver',
    'red', 'pink', 'brown', 'orange',
    'olive', 'yellow', 'green', 'lime',
    'blue', 'aqua', 'purple', 'magenta'
]

function createDialog(attrs){
    let modal = $('<div></div>').addClass('modal').attr(
        {
            role:'dialog',
            'aria-labelledby':'modalTitle',
            'aria-hidden':'false'
        });
    let dialog  = $('<div></div>').addClass('modal-dialog modal-dialog-centered').appendTo(modal);
    let content = $('<div></div>').addClass('modal-content').appendTo(dialog);
    let header = $('<div></div>').addClass('modal-header').appendTo(content);
    $('<h5></h5>').addClass('modal-title').text(attrs.name + ' Change').attr('id', 'modalTitle').appendTo(header).append(
        $('<button></button').addClass('close').attr({
            type:'button',
            'data-dismiss':'modal',
            'aria-label':'Close',
        }).append(
            $('<span></span>').attr('aria-hidden', true).text('&times;')
    ));
    let body = $('<div></div>').addClass('modal-body').appendTo(content);
}

$(document).ready(() =>{
    //tooltips       
    $('[data-toggle="tooltip"]').tooltip();
   
})

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