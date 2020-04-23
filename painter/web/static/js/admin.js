const SPINNER_DOM = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'

const PlaceButtonTexts = [
	'Turn Place Off',
	'Turn Place Off',
	'<span class="spinner spinner-border spinner-border-md" role="status" aria-hidden="true"></span>',
	'Error'
]

/**
 * @param {Number} new_state 
 * @summary updates the place_button for its new state
 */
function ChangeLockButton(new_state) {
	let lock_button = $('#place-button')
	if(_.isNull(new_state)){
		lock_button.children('h6').text('Tries again in 10 seconds');
		lock_button.attr('state', 2);

	} else {
		lock_button.attr('state', new_state ? 1 : 0);
		lock_button.children('h6').text(new_state ? 'Turn Place Off' : 'Turn Place On');
	}
}

let currently_refreshes = false;
/**
 * @function
 * @param {_repeat} number to repeat the tas
 * @returns checks again the button state
 * sends ajax request to check if the lock state
 */
const refreshButtonState = (_stack=0, _ignore_refresh=false) => {
	if(currently_refreshes || !_ignore_refresh){
		return;
	}
	if(!currently_refreshes){
		currently_refreshes = true;
	}
	function _refreshAgain(){
		// change lock button
		if(_stack > 5){
			// if its null
			_.delay(
				10000,	// 10000 ms
				() => refreshButtonState(_stack + 1, true)
			)
		} else {
			// change lock button
			ChangeLockButton(3);
			currently_refreshes = false;
		}
	}
	// change lock button state to 2;
	ChangeLockButton(2)

	$.ajax({
		url:'/get-active-state',
		method:'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(lock_state){
			if(_.isNull(lock_state)){
				ChangeLockButton(2);
			} else {
				ChangeLockButton(new_state ? 1 : 0);
			}
			
		}
	}).catch(_refreshAgain)
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
		if(board_state == '2'){
			Swal.fire({
				icon:'error',
				title:"Waiting for request answer",
				text:"Waiting for server give the data about the lock"

			})
		} else {
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
		}
	})
});