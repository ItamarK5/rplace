const EXAMPLE_PRIVATE_KEY = "MIICXgIBAAKBgQCpVEzdoTm5kJc3QEMi+8Cz7Pv5V2DQTWXs8iw4xJCU5MiPnH1ggZTqbNmKicUr6dQig6qNbIAhG4UuwAFih3FJ4MwkDVlL6ZD4TK+TZicaW9rgrMIcy0dWpvoLKddCqDN7ANr7FsD1o6p6bvmf2d14d6rswrz/+/Ih0BdHnmXBrwIDAQABAoGBAILMW5PXtn9g8W38dd/QGErkBL/WfzJolxMw/nfbXtOk5kgI2dBySFXNPz2Eron9VaBTlKsp5M+uMnKqXmd9uEPSuvLM5pk3fuulAOz/5OtZnt1hxd4ZQpzEvl2uWqFr1yiIJE1vbe4EyCa8UKUeaNDz4FRPkiFUUOEBYGMdtswBAkEA9ytTJwEfTJo+DXoI5jRT616DBOrGwcteMVKqIbf3BTnHWEZ2UoNvqoj3ENQgouDyGGxhAaDoiaf0veW5coy1JwJBAK9hB+EJqRAO0ql2LZxWj8Bfm3fDmDndb9iM/XKjlbe512ykRJX7rOCVeu411WOUEq/nxMvrTFRCyUweRqf+tDkCQD4lWIzwDUyXY47D5kTrV0ZQxySPW1YSqiZAoKJFvQhFVMfvP4TTo1n/gg9rJqGNaZGWfnWIXa9u2Wx9vDj/A/UCQQCl+8WDPKtfYUgLzqd4UYyX22S+wsWt7l/OqhGtkBlA24iBcC7hbGK/43mHPjgJmLje9xIQlU+WZ+cwPW9NzAgxAkEAk655nA0vLKfYHXXLb25TOF8xiHyq7lawx3wm7nEcfRlz2QP0Ouk0GGBc54f/I6L+fdwVto+S7fqxMMXEU/kbkA=="
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