$(document).ready(function(){
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
  $('.form-control').keypress((e) => {
    if(e.charCode == 13 && !e.shiftkey){  // enter key
      e.preventDefault();
      let form_controls = $('.form-control');
      let idx = _.indexOf(form_controls, event.currentTarget)+1;
      if(idx == form_controls.length){
          $('#submit-button').focus();
      } else {
        $(form_controls[idx]).focus();
      }
    }
  });
  $('.form-control').first().focus();
});