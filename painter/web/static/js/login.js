/**
 * @auther Itamar Kanne
 * @file contain extra code for the login page specific
 */

/**
	* @param {HTMLCheckboxButton} button button html object pressed
	* shows an message related to the remember me button
 */
function RememberMeMessage(button) {
  // if cookies are enabled message
	if(navigator.cookieEnabled){
	  Swal.fire({
		icon:'warning',
		title:'Security Warning',
		text:'Are your sure? It might make your account more vulnerable to attacks'
	  })
	// if cookies aren't enabled message
	} else {
	  Swal.fire({
		icon:'error',
		title:'Cookies required',
		html:`You need to enable cookies in your browser before allowing.To learn how to enable them\
		<a href="https://www.whatismybrowser.com/guides/how-to-enable-cookies/auto">Click Here</a>`
	  }).then(() => {
		if(!navigator.cookieEnabled){
		  button.checked = false;
		}
	  })
	}
} 

$(document).ready(function(){
	// applied only once
	let remember_message = _.once(RememberMeMessage)
	$('#remember').change(function() {
		if(this.checked){
		  remember_message(this);
		}
	});
});