$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    $('#submit-button').click(function(e) {
        e.preventDefault();
        this.innerHtml = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Loading...'
        // also change passwords back to normal
        $('.password-button').parent().siblings('input').attr('type', 'password');
        // submit form
        $('form').submit();
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
    // focus .form-control
    $('form').submit((e) =>{
        e.preventDefault();
        console.log(5)
        firebase.auth().setPersistence(firebase.auth.Auth.Persistence.SESSION)
            .then(function() {
                // Existing and future Auth states are now persisted in the current
                // session only. Closing the window would clear any existing state even
                // if a user forgets to sign out.
                // ...
                // New sign-in will be persisted with session persistence.
                return firebase.auth().signInWithEmailAndPassword(
                    $('input[name="username"]').val(),
                    $('input[name="password"]').val()
                );
            })
            .catch(function(error) {
                // Handle Errors here.
                let errorCode = error.code;
                let errorMessage = error.message;
                console.log(errorCode, errorMessage);
                $('#submit-button')[0].innerHtml = 'Login'
            })
    });          
});

$(window).on('load', () => {
    $('.form-control').first().focus();
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            firebase.auth().currentUser.getIdToken(/* forceRefresh */ true).then(function(idToken) {
                // generating form
                let form = $('<form></form>').append($('<input>').attr({
                    type:'hidden',
                    value:$('input[name="csrf_token"]').val(),
                    name:'csrf_token'
                })).append($('<input>').attr({
                    type:'text',
                    value:idToken,
                    name:'token'
                }))
                console.log(form.children())
                $.ajax({
                    url:$('form').attr('action'),
                    method:$('form').attr('method'),
                    data:form.serialize(),
                    success: resp => {
                        console.log(resp);
                    }
                });
              }).catch(function(error) {
                // Handle error
                console.log(error);
              });
        }
    });  
})
