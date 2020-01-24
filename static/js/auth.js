$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
  $('#submit-button').click(function(e){
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
});