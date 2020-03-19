Boolean.prototype.toInt = function() { return this.valueOf() ? 1 : 0; }

function ChangeLockButton(new_state) {
	let lock_button = $('#place-button')
  	text = `The place is ${new_state ? 'unpause' : 'pause'}`;
  	lock_button.attr('state', new_state.toInt().toString());
  	lock_button.children('h6').text(new_state ? 'Turn Place Off' : 'Turn Place On')
}

const sock = io('/admin', {transports:['websocket']})
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
				sock.emit('change-lock-state', board_state  == '0', (callback) => {
					if(callback.success){
						ChangeLockButton(callback.response);
					}
					Swal.fire({
						title: callback.success ? `App is ${callback.response ? 'paused' : 'unpause'}` : 'Error!',
						icon:  callback.success ? 'success' : 'error',
						text: callback.success ? 'You lock/unlock board for all users' : callback.response
					});
				});
			}
		})
	});
	sock.on('set-lock-state', (callback) => {
		alert('hello')
		if(callback){
			return;
		}
	})
});