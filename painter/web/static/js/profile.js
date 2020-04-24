/** @constant BLACK_INDEX index of the black color, special one */
const BLACK_INDEX = 1;
/** @constant {jQuery} ColorPicker jquery reference to color picker */
const ColorPicker = $('#color')
/** @constant COLORS the palette of the board to decide favorite button */
const COLORS = [
    'White', 'Black', 'Gray', 'Silver',
    'Red', 'Pink', 'Brown', 'Orange',
    'Olive', 'Yellow', 'Green', 'Lime',
    'Blue', 'Aqua', 'Purple', 'Magenta'
]

/**
 * 
 * @param {number|string} id id of field to change its value
 * @param {number} val value to convert form
 * @return {string|number} converted the value
 * @desc handles color option and url option to fix for specific options
 */
const valueConvertor = (id, val) => {
    switch(id){
        case 'color':
            // number
            return COLORS[val]  // select specific color
        case 'url':
            // strings
            return val ? val : 'None'   // nothing becomes null
        default:
            // number
            return val
    }
}

/**
 * 
 * @param {jQuery} modal_query jquery object the reference 1 query
 * @param {boolean} success_or_error if for success or error
 * @returns {HTMLElement} hml element the messages if the change to the value succeeded or got error
 */
const getModalMessageElement = (modal_query, success_or_error) => $(`#${modal_query.attr('id')} .if-${success_or_error}`);

/**
 * 
 * @param {jQuery} query children of a modal objects
 * @returns {jQuery} returns jQuery of holding the parent modal of the object, otherwise returns empty jQuery
 */
const getModalParent = (query) => query.parents('.modal').first();

/**
 * 
 * @param {jQuery} jquery_ele 1
 * @param {*} idx index of color
 * @desc
 * sets the background and color of the object, color of text is
 * changed if the selected color is black (to white) and if switched from black then 
 * text color returns to black
 */
const setColorSelector = (jquery_ele, idx) => {
    jquery_ele.css('background-color', COLORS[idx].toLowerCase());
    jquery_ele.css('color', () => idx ==  BLACK_INDEX ? 'white': 'black')
}
/**
 * @desc updates the color field for the specific selected color choice
 */
const updatePickColor = () => {
    // color field select
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
    updatePickColor();
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
    // when a setting form object is submitted
    $('.setting-form').submit(function(e){
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
                    // get the item
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
            error: (xmlhttprequest) =>{
                // read later https://stackoverflow.com/a/3543713
                Swal.fire({
                    icon:'error',
                    title:'Error',
                    html:xmlhttprequest.responseText
                });
            }
        });
    })
});