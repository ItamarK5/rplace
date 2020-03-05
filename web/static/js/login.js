
$(document).ready(function(){
  const encrypt = new JSEncrypt();
  encrypt.setPublicKey(PRIVATE_KEY);
    $('[data-toggle="tooltip"]').tooltip();
    $('#submit-button').click(function(e) {
        this.innerHTML='<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...';
        // also change passwords back to normal
        $('.password-button').parent().siblings('input').attr('type', 'password');
        // submit form
        $('form').submit()
    });
    $('.password-button').click(function(e){
        e.preventDefault();
        if($(this).children('i').hasClass('fa-eye-slash')){   // if is hidden, remove slashed eye
            $(this).parent().siblings('input').attr('type', 'password');
            $(this).children('i').removeClass('fa-eye-slash').addClass('fa-eye')
        } else {
          $(this).parent().siblings('input').attr('type', 'text');
          $(this).children('i').removeClass('fa-eye').addClass('fa-eye-slash');
        }
    });
    // cool feature, when press enter gets next control
    $('.form-control').keypress((e) => {
      if(e.charCode == 13 && !e.shiftkey){  // enter key
        e.preventDefault();
        let form_controls = $('.form-control');
        // find index of next character
        let idx = _.indexOf(form_controls, event.currentTarget)+1;
        if(idx == form_controls.length){
            $('#submit-button').focus();
        } else {
          $(form_controls[idx]).focus();
        }
      }
    });
    $('.form-control').first().focus();
    $('#remember').change(function() {
      if(this.checked){
        if(navigator.cookieEnabled){
          Swal.fire({
            icon:'warning',
            title:'Security Warning',
            text:'Are your sure? It might make your account more vulnerable to attacks'
          })
        } else {
          Swal.fire({
            icon:'error',
            title:'Cookies required',
            html:'You need to enable cookies in your browser before allowing.\nTo learn how to enable them <a href="https://www.whatismybrowser.com/guides/how-to-enable-cookies/auto">Click Here</a>'
          }).then(() => {
            if(!navigator.cookieEnabled){
              this.checked = false;
            }
          })
        }
      }
    });
    /*$('form').first().submit(function(e){
      // prevent default
      e.preventDefault()
      // now form control should 
      let encrypt_form = $('<form>').attr({
        id:'encrypt_form'
        url:this.getAttribute('url'),
        method:this.getAttribute('method')
      });
      //https://stackoverflow.com/a/4291032
      $(`form#${this.getAttribute('id')} :input`).each(
        (idx, ele) => {
          $(ele).clone().appendTo(encrypt_form[0])
        }
      )
      $(`form#${encrypt_form.attr('id')} :input`).each(
        (idx, ele) => {
        if($(ele).val() instanceof String){
          $(ele).val(btoa(encrypt.encrypt($(ele).val())))
        }
      })
      console.log($(encrypt_form));
      setTimeout(() =>$(encrypt_form).submit(), 2000)
    })*/
  });