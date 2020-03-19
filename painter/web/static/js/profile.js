const FORM_INPUT = '#setting-input'
const GET_FIELD = /.+(?=-active)/i
// minimal title regex to find all non-upper characters after space or nothing
const ToTitleCaseRegex = /(<=\x20|^)[a-z]/g;
const COLORS = [
    'white', 'black', 'gray', 'silver',
    'red', 'pink', 'brown', 'orange',
    'olive', 'yellow', 'green', 'lime',
    'blue', 'aqua', 'purple', 'magenta'
]

const SettingDescriber = $('#setting-describer');
/**
 * 
 * @param {String} clr 
 * @returns {object} object
 */
function setColor(clr){
    return {
        'background-color':clr,
        color:clr != 'black' ? 'black' : 'white'    
    }
}

String.prototype.toTitleCase = function(){
    return this.replace(ToTitleCaseRegex, (str) => str.toUpperCase())
}

const hideModalAlert = () => $('#setting-alert').hide();
/**
 * 
 * @param {HTMLFormElement} form 
 * @param {String} val 
 */
function AddUlrInput(form, val){
    let group = $('<div></div>').addClass('input-group input-group-default').attr('id', FORM_INPUT.slice(1)+'-father').appendTo(form)
    $('<input>').attr({
        id:FORM_INPUT.slice(1),
        name:'url',
        class:'form-control',
        value:val == 'None' ? '' : val,
        type:'text',
    }).on('input', function(e){
        hideModalAlert();
    }).appendTo(group);
    let append_group = $('<div></div>').addClass('input-group-append').appendTo(group);
    let btn = $('<button></button>').addClass('btn btn-outline-secondary').attr('type', 'button').appendTo(append_group);
    $('<span></span>').addClass('fas fa-trash-alt').appendTo(btn);
    btn.click(function(e){
        $(FORM_INPUT).val('');
        e.preventDefault();
    });
    $('#row-describer').hide();
}

/**
 * 
 * @param {HTMLFormElement} form 
 * @param {String} field 
 * @param {any} val 
 * add input to the form depending the value of field
 */
function addForm(form, field, val){
    switch(field){
        case 'x': {
            SettingDescriber.show()
            SettingDescriber.text(val);
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'x',
                class:'form-control-range',
                min:0,
                max:999,
                value:parseInt(val),
                type:'range',
            })
            .addClass('form-control-range')
            .change(function(e){
                SettingDescriber.text(this.value);
                hideModalAlert();
            }).appendTo(form);
            SettingDescriber.text(val);            
            break;
        }
        case 'y':{
            SettingDescriber.show();
            SettingDescriber.val(val)
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'y',
                min:0,
                max:999,
                value:parseInt(val),
                type:'range',
            })
            .addClass('form-control-range')
            .change(function(){
                SettingDescriber.text(this.value);
                hideModalAlert();
            }).appendTo(form);
            SettingDescriber.text(val)
            break;
        }
        case 'scale': {
            SettingDescriber.show()
            SettingDescriber.text(val);
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'scale',
                min:1,
                max:50,
                value:parseInt(val),
                type:'range',
            }).addClass('form-control-range').change(function(){
                SettingDescriber.text(this.value.toString());
                hideModalAlert()
            }).appendTo(form);
            SettingDescriber.text(val.toString())
            break;
        }
        case 'color': {
            SettingDescriber.hide()
            let color_selector = $('<select>').attr({
                id:FORM_INPUT.slice(1),
                name:'color',
            }).addClass('custom-select').appendTo(form);
            COLORS.forEach(
                (color_val,idx) => {
                    let option = $('<option></option>').css(setColor(color_val)).attr('value',idx).text(color_val).appendTo(color_selector);
                    if(val == color_val){
                        option.attr('selected', '');
                    }
                    
            });
            $('#row-describer').hide();
            break;
        }
        case 'url': {
            SettingDescriber.hide()
            AddUlrInput(form, val);
            break;
        }
        default:{
            
            break;
        }
    }
}

function filterResponse(field, val){
    if(field == 'color'){
        return COLORS[val];
    } else if(field == 'url'){
        return val == '' ? 'None' : val;
    } else {
        return val;
    }

}

function onShowingEditPreferencesModal(button, modal){
    let field = GET_FIELD.exec(button.attr('id'))[0];
    if(field == null){
        modal.hide();
    }
    $(FORM_INPUT+'-father').remove()
    $(FORM_INPUT).remove()
    $('#modal-title').text(`Change ${field}`);
    addForm($('#setting-form'), field, button.parent().siblings('.setting-val').children('h5').text())
    $('#setting-alert').hide()
}
const sock = io('/profile');
$(document).ready(() =>{
    //tooltips       
    $('#modal-change-preference').on('shown.bs.modal', function (event) {
        console.log(event);
        $('#row-describer').show();
        let button = $(event.relatedTarget ? event.relatedTarget : $('button:hover')[0]);
        console.log(button)
        let modal = $(this);
        onShowingEditPreferencesModal(button, modal);
    })
    //submit form
    $('#save-setting').click(function(e) {
        $('#setting-form').submit();
    });
    //first name change
    $('#setting-form').submit(function(e){
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url:form.attr('action'),
            type:form.attr('method'),
            data:form.serialize(),
            success: (response) => {
                console.log(response)
                $('#setting-alert')
                    .show()
                    .text(response.success ? 'Changed Successfully' : response.errors.join('\n'))
                    .addClass(response.success ? 'alert-success' : 'alert-danger')
                    .removeClass(response.success ? 'alert-danger' : 'alert-success');
                if(response.success){
                    $(`#text-${response.id}`).text(filterResponse(response.id, response.val));
                }
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