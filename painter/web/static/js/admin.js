/**
 * @name ToInt
 * @returns integer form
 */
Boolean.prototype.toInt = function() { return this.valueOf() ? 1 : 0; }

/**
 * @name ChangeLockButton
 * @param {Number} new_state 
 * @summary updates the place_button for its new state
 */
function ChangeLockButton(new_state) {
	let lock_button = $('#place-button')
  	text = `The place is ${new_state ? 'unpause' : 'pause'}`;
  	lock_button.attr('state', new_state.toInt().toString());
  	lock_button.children('h6').text(new_state ? 'Turn Place Off' : 'Turn Place On')
}

// creates the io object
const sock = io('/admin')

/**
 * @name refreshButtonState
 * @returns checks again the button state
 */
refreshButtonState => {
	$.ajax({
		url:'/get-active-state',
		method:'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(lock_state){
			ChangeLockButton(JSON.parse(lock_state));
		}
	})
}

// refresh the button on connection
sock.on('connect', () => {
	refreshButtonState();
});
// 
sock.on('set-lock-state', (callback) => {
	ChangeLockButton(callback)
});
sock.on('reconnect', () => 	refreshButtonState());
sock.on('reconnect_error', () =>{
	Swal.fire({
		icon:'error',
		title:'Server Not Found',

	})
})

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