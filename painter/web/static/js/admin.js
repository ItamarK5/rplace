Boolean.prototype.toInt = function() { return this.valueOf() ? 1 : 0; }

function ChangeLockButton(new_state) {
	let lock_button = $('#place-button')
  	text = `The place is ${new_state ? 'unpause' : 'pause'}`;
  	lock_button.attr('state', new_state.toInt().toString());
  	lock_button.children('h6').text(new_state ? 'Turn Place Off' : 'Turn Place On')
}

const sock = io('/admin')

function refresh_button_state(){
	$.ajax({
		url:'/get-active-state',
		method:'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(lock_state){
			ChangeLockButton(JSON.parse(lock_state));
		}
	})
}

sock.on('connect', () => {
	refresh_button_state()
});
sock.on('set-lock-state', (callback) => {
	ChangeLockButton(callback)
});
sock.on('reconnect', () => 	refresh_button_state());


$(document).ready(() => {
	sock.connect()
	$('[data-toggle="tooltip"]').tooltip();
	$('tr').click(function() {
		let name = $(this).children('.name-col').text();
		if(name){
			window.location.href = `/edit/${$(this).children('.name-col').text()}`
		};
	});
	$('#place-button').click(function(){
		let board_state = $(this).attr('state');
		Swal.fire({
			title: 'Are you sure?',
			text: `You want to ${board_state == "1" ? "pause" : "unpause"} the place`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
		}).then((result) => {
			if (result.value) {
				$.ajax({
					url:'/change-lock-state',
					method:'POST',
					contentType:'application/json;charset=UTF-8',
					data:board_state,
					success:function(message){
						Swal.fire({
							title: message.success ? `App is ${message.text ? 'paused' : 'unpause'}` : 'Error!',
							icon:  message.success ? 'success' : 'error',
							text: message.success ? 'You lock/unlock board for all users' : message.text
						});
					},
					error:(error) => {
						console.log(error)
						Swal.fire({
							icon:'error',
							title:error.statusText ? '' : 'Error',
							html:error.responseText
					})}
				})
			}
		})
	});
});