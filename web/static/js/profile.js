const FORM_INPUT = '#setting-input'
const GET_FIELD = /.+(?=-active)/i
const COLORS = [
    'white', 'black', 'gray', 'silver',
    'red', 'pink', 'brown', 'orange',
    'olive', 'yellow', 'green', 'lime',
    'blue', 'aqua', 'purple', 'magenta'
]


function setColor(val){
    return {
        'background-color':val,
        color:val != 'black' ? 'black' : 'white'    
    }
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
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'x',
                class:'form-control-range',
                min:0,
                max:999,
                val:parseInt(val),
                type:'range',
            }).change(function(e){
                $('#setting-describer').text(this.value);
            }).appendTo(form);
            $('#setting-describer').text(val)
            break;
        }
        case 'y':{
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'y',
                class:'form-control-range',
                min:0,
                max:999,
                val:parseInt(val),
                type:'range',
            }).change(function(e){
                $('#setting-describer').text(this.value);
            }).appendTo(form);
            $('#setting-describer').text(val)
            break;
        }
        case 'scale': {
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'scale',
                class:'form-control-range',
                min:1,
                max:50,
                val:parseInt(val),
                type:'range',
            }).change(function(e){
                $('#setting-describer').text(this.value);
            }).appendTo(form);
            $('#setting-describer').text(val)
            break;
        }
        case 'color': {
            let color_selector = $('<select>').attr({
                id:FORM_INPUT.slice(1),
                name:'scale',
                class:'custom-select',
                value:parseInt(val),
            }).change(function(e){
                $('#setting-describer').text(COLORS[this.value]);
            }).appendTo(form);
            COLORS.forEach(
                (val,idx) => {
                    let option = $('<option></option>').css(setColor(val)).attr('value',idx).text(val).appendTo(color_selector);
                    if(idx == val){
                        option.attr('selected', '');
                    }
            });
            $('#setting-describer').text(COLORS[val]);
            break;
        }
        case 'url': {
            $('<input>').attr({
                id:FORM_INPUT.slice(1),
                name:'url',
                class:'form-control-text',
                val:val,
                type:'url',
            }).change(function(e){
                $('#setting-describer').text(this.value ? this.value : '');
            }).appendTo(form);
            $('#setting-describer').text(val)
            break;
        }
        default:{
            break;
        }
    }
}

$(document).ready(() =>{
    //tooltips       
    $('[data-toggle="tooltip"]').tooltip();
    $('.modal').on('shown.bs.modal', function (event) {
        let button = $(event.relatedTarget);
        let modal = $(this);
        let field = GET_FIELD.exec(button.attr('id'))[0];
        if(field == null){
            modal.hide();
        }
        $(FORM_INPUT).remove()
        $('#modal-title').text(`Change ${field}`);
        addForm(
            $('#setting-form'), field,
            button.parent().siblings('.setting-val').children('h5').text())
        }
    );
    $('#save-setting').click(function(e) {
        e.preventDefault();
        let form = $('#setting-form');
        $.ajax({
            url:form.attr('action'),
            type:form.attr('method'),
            data:form.serialize(),
            success: (data) => {
                console.log(6);
                return;
            },
            error: (data) =>{
                console.log(5);
            }
        });
    $('#color').once({
        
    })
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