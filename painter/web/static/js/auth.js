/**
 * @auther Itamar Kanne
 * @file this file includes all javascript code in an authentication page (sign in, sign up, forgot password, revoke password and more)
 */
/**  @const LOADING_HTML_TEXT spinner of html text, while sending a request*/
const LOADING_HTML_TEXT = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...'

// ready function
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
  $('#submit-button').click(function(e) {
	  this.innerHTML=LOADING_HTML_TEXT;
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
  /** on keypress */
  $('#submit-form .form-control').keypress((e) => {
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
  // focus on first form control shown
  $('#submit-form .form-control').first().focus();
});
