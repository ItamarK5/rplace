const SPINNER_HTML = '<span class="spinner-border spinner-border-sm role="status" aria-hidden="true"></span>Loading...'
function rememberMeMessage(button) {
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
    let remember_message = _.once(rememberMeMessage)
    $('#remember').change(function() {
        if(this.checked){
          remember_message(this);
        }
    });
  });