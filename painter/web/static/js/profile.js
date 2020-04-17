const BLACK_INDEX = 1;
const ColorPicker = $('#color')
const COLORS = [
    'White', 'Black', 'Gray', 'Silver',
    'Red', 'Pink', 'Brown', 'Orange',
    'Olive', 'Yellow', 'Green', 'Lime',
    'Blue', 'Aqua', 'Purple', 'Magenta'
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

const getModalMessageElement = (modal_query, success_or_error) => $(`#${modal_query.attr('id')} .if-${success_or_error}`);
const getModalParent = (query) => query.parents('.modal').first();

const setColorSelector = (jquery_ele, idx) => {
    jquery_ele.css('background-color', COLORS[idx].toLowerCase());
    jquery_ele.css('color', () => idx ==  BLACK_INDEX ? 'white': 'black')
}
const colorSelector = () => {
    ColorPicker.children().each(function(idx) {
        let ele = $(this);
        setColorSelector(ele, idx)
        if(ele.attr('val') == ColorPicker.val()){
            setColorSelector(ColorPicker, idx)
        }
    })
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
    $('#color').attr('selected', $(`#color > option:contains('${$('#text-color').text()}')`).attr('value'));
    colorSelector();
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
            console.log(result)
            if(result.value){
                $(`${$(button).attr('data-target')}`).val('')
            }
        })
    })
    $('.setting-form').submit(function(e){
        console.log(5)
        e.preventDefault();
        let form = $(this);
        let parent = getModalParent(form);
        let success_div = getModalMessageElement(parent, 'success');
        let error_div = getModalMessageElement(parent, 'error');
        success_div.addClass('d-none');
        error_div.addClass('d-none');
        error_div.children().remove();
        console.log(parent)
        $.ajax({
            url:form.attr('action'),
            type:form.attr('method'),
            data:form.serialize(),
            success: (response) => {
                message_element = response.success ? success_div : error_div;
                message_element.removeClass('d-none')
                if(response.success){
                    $(`*[aria-describedat='#${response.id}']`).text(valueConvertor(response.id, response.val));
                    error_div.addClass('d-none')
                    success_div.removeClass('d-none')
                } else {
                    success_div.addClass('d-none')
                    error_div.removeClass('d-none')
                    response.errors.forEach(val => {
                        $('<ul></ul>').addClass('list-group-item list-group-item-danger').text(val).appendTo(error_div[0])
                    });
                }
                
            },
            error: (err) =>{
                // read later https://stackoverflow.com/a/3543713
                Swal.fire({
                    icon:'error',
                    title:'Error',
                    html:err.responseText
                });
            }
        });
    })
});