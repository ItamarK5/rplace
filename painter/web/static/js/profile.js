const COLORS = [
    'white', 'black', 'gray', 'silver',
    'red', 'pink', 'brown', 'orange',
    'olive', 'yellow', 'green', 'lime',
    'blue', 'aqua', 'purple', 'magenta'
]

const valueConvertor = (id, val) => {
    switch(id){
        case 'color':
            return COLORS[val]
        case 'url':
            return val ? val : 'None'
        default:
            return val
    }
}

$(document).ready(() =>{
    //tooltips       
    //submit form
    $('.commit-setting').click(function(e) {
        console.log(this)
        $(`${$(this).attr('data-target')} form`).submit();
        console.log($(`${$(this).attr('data-target')} form`))
        e.preventDefault();
    });
    //first name change
    $('.form-control-range').change(function(e){
        $(`*[field-related="#${this.getAttribute('id')}"]`).text($(this).val())
    });
    $('#delete-url').click(function() {
        let button = this;
        Swal.fire({
            icon:'warning',
            title:'Are you sure?',
            text:'Are you sure you want to erase the url?',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
        }).then((result) => {
            if(result.value){
                $(`${$(button).attr('data-target')}`).val('')
            }
        })
    })
    $('.setting-form').submit(function(e){
        console.log(5)
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url:form.attr('action'),
            type:form.attr('method'),
            data:form.serialize(),
            success: (response) => {
                console.log(response)
                console.log(`*[aria-describedat='#${response.id}']`)
                let r = $(`*[aria-describedat='#${response.id}']`);
                console.log(r)
                r.text(valueConvertor(response.id, response.val))
            },
            error: (data) =>{
                // read later https://stackoverflow.com/a/3543713
                console.log(data)
            }
        });
    })
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