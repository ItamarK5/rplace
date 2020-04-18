/**
 * @returns integer form
 */
Boolean.prototype.toInt = function() { return this.valueOf() ? 1 : 0; }

/**
 * @param {Number} new_state 
 * @summary updates the place_button for its new state
 */
function ChangeLockButton(new_state) {
	let lock_button = $('#place-button')
  	lock_button.attr('state', new_state.toInt().toString());
  	lock_button.children('h6').text(new_state ? 'Turn Place Off' : 'Turn Place On')
}


/**
 * @function
 * @returns checks again the button state
 * sends ajax request to check if the lock state
 */
const refreshButtonState = () => {
	$.ajax({
		url:'/get-active-state',
		method:'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(lock_state){
			ChangeLockButton(JSON.parse(lock_state));
		}
	})
}
// creates the io object
/**
 * @const {SocketIO} sock
 * socket
 */
const sock = io('/admin');
/**
 * @name connect
 * @summary refresh button state when connects to server
 */
sock.on('connect', () => {
	refreshButtonState();
});
/**
 * @name set-lock-state
 * @summary sets the lock state of the board
 */
sock.on('set-lock-state', (callback) => {
	ChangeLockButton(callback)
});
/**
 * @name reconnect
 * @summary sets the lock state of the board
 */


/**
 * @const throttleIOMessageTimeout timeout in milliseconds until need to call again that found no connection
 */
const throttleIOMessageTimeout = 5000;


/**
 * @namespace
 * @desc handles server not found responses
 */
const ServerReporter = {
	/**
	 * @name force_connection_message
	 * @memberof ServerReporter
	 * @type {boolean}
	 * @desc if to show connection message
	 */
	force_connection_message : false,
	messageConnectionError() {
		Swal.fire({
			icon:'error',
			title:'Server Not Found',
		});
	},
	/**
	 * @private
	 * wraps the message connection error, so it will be send 5 minutes after
	 * last try
	 */
	__throttleMessageConnection: null,
	/**
	 * reports on reconnection
	 */
	onReconnectionError(){
		if(this.reconnection_message){
			force_connection_message = true;
			this.__throttleMessageConnection = _.throttle(this.messageConnectionError, {leading:false})
			this.throttleMessageConnection();
		}
		this.__throttleMessageConnection()
	}
}

sock.on('reconnect', () => 	refreshButtonState());
sock.on('reconnect_error', () => ServerReporter.onReconnectionError())




//ready function
$(document).ready(() => {
	sock.connect()
	//@ts-ignore
	$('[data-toggle="tooltip"]').tooltip();

	// click row
	$('tr').click(function() {
		let name = $(this).children('.name-col').text();
		if(name){
			window.location.href = `/edit/${$(this).children('.name-col').text()}`
		};
	});
	// click place
	$('#place-button').click(function(){
		let board_state = $(this).attr('state');
		// swal message to check if user is sure
		Swal.fire({
			title: 'Are you sure?',
			text: `You want to ${board_state == "1" ? "pause" : "unpause"} the place`,
			icon: 'warning',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
		}).then((result) => {
			if (result.value) {
				$.post({
					url:'/change-lock-state',
					contentType:'application/json;charset=UTF-8',
					data:board_state,
					success:function(message){
						Swal.fire({
							title: message.success ? `App is ${message.text ? 'paused' : 'unpause'}` : 'Error!',
							icon:  message.success ? 'success' : 'error',
							text: message.success ? 'You lock/unlock board for all users' : message.text
						});
					},
				}).catch((error) => {
					Swal.fire({
						icon:'error',
						title:error.statusText ? '' : 'Error',
						html:error.responseText
					})
				})
			}
		})
	});
});