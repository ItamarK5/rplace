/**
 * @auther Itamar Kanne
 * @file this file includes all staff related to the admin page
 */

/** @const MAX_SIZE the maximum number of attempt before considers fail */
const MAX_STACK = 5;
/** @const DELAY_REFRESH_ATTEMPT the number of ms between each retry to refresh */
const DELAY_REFRESH_ATTEMPT = 5000;
/** @const AppEnableSwitchTexts an array holding the texts of the the button depending its state*/
const AppEnableSwitchTexts = [
	'Turn Place On',
	'Turn Place Off',
	'<span class="spinner spinner-border spinner-border-md" role="status" aria-hidden="true"></span>',
	'Error'
]

/**
 * @param {Number} new_state 
 * @summary updates the place_button for its new state
 */
function changeLockState(new_state) {
	let lock_button = $('#place-button')	
	lock_button.attr('state', new_state);
	lock_button.children('h6').html(AppEnableSwitchTexts[new_state]);
}

/**
 * @name isErrorResponse
 * @param {Any} xhr anything but suppose to be xhr object
 * @return {Boolean} if its a 404 response (not found)
 * checks if response is XMLHttpResponse with status 404
 */
const isErrorResponse = (xhr) => (xhr instanceof XMLHttpRequest) && xhr.has(xhr, 'status') && (xhr.status % 100 == 4 || xhr.status % 100 == 5);


let currently_refreshes = false;
/**
 * @function
 * @param {number} _stack the number of times called the command
 * @returns checks again the button state
 * sends ajax request to check if the lock state
 */
const refreshButtonState = (_stack=0) => {
	if(currently_refreshes){
		return;
	}
	if(!currently_refreshes){
		// prevent multiple attempts
		currently_refreshes = true;
	}
	/**
	 * @private
	 * @function
	 * @param {XMLHttpRequest} error the xml http object of the error response
	 * a utility function of new refresh attempt 
	 */
	function _refreshAgain(error){
		console.log(error)
		// change lock button
		if(_stack > MAX_STACK){
			// if its null
			Swal.fire({
				icon:'warning',
				title:  error.statusText ? error.statusText : 'Fail to connect',
				text: error.responseText ? error.responseText : 'Fail to collect data from the server',
				allowOutsideClick: false // prevent outside clicks
			}).then(
				_.delay(
					() => refreshButtonState(_stack + 1, true),
					DELAY_REFRESH_ATTEMPT
				)
			)
		} else {
			// change lock button
			changeLockState(3);
			currently_refreshes = false;
		}
	}
	// change lock button state to 2;
	changeLockState(2)

	$.ajax({
		url:'/is-board-locked',
		method:'GET',
		contentType:'application/json;charset=UTF-8',
		success: function(response){
			if(isErrorResponse(response)){
				_refreshAgain(response)
			}
			else {
				changeLockState(response ? 1 : 0);
			}
			
		}
	}).catch(_refreshAgain)
}
// creates the io object
/**
 * @const {SocketIO} sock
 * socket connected to admin namespace
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
	changeLockState(callback)
});
/**
 * @const throttleIOMessageTimeout timeout in milliseconds until need to call again that found no connection
 */
const throttleIOMessageTimeout = 5000;
/**
 * @name hasEncounteredError
 * @param {XMLHttpRequest} xhr 
 * @return {Boolean} if its an error response
 * checks if response is XMLHttpResponse, error xml responses have status codes 4xx and 5xx
 */
const isErrorStatus = (xhr) => xhr instanceof XMLHttpRequest && _.has(xhr, 'status') && xhr.status % 100 == 4 && xhr.status % 100 == 5;

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
	$('tr:parent(#users-table)').click(function() {
		let name = $(this).children('.name-col').text();
		if(name){
			window.location.href = `/edit-user/${$(this).children('.name-col').text()}`
		};
	});
	// click place
	$('#place-button').click(function(){
		let board_state = $(this).attr('state');
		console.log(parseInt(board_state))
		// swal message to check if user is sure
		switch(parseInt(board_state)){
			// has value
			case 1:
			case 0:{
				Swal.fire({
					title: 'Are you sure?',
					text: `You want to ${board_state == "1" ? "pause" : "unpause"} the place`,
					icon: 'warning',
					showCancelButton: true,
					confirmButtonColor: '#3085d6',
					cancelButtonColor: '#d33',
				}).then((result) => {
					if (result.value) {
						// post change
						$.post({
							url:'/change-lock-state',
							contentType:'application/json;charset=UTF-8',
							data:board_state,
							success:function(message){
								Swal.fire({
									title: message.success ? `App is ${message.text ? 'paused' : 'unpause'}` : 'Error!',
									icon: message.success ? 'success' : 'error',
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
				break;	
			}
			case 2:{
				Swal.fire({
					icon:'info',
					title:'Wait',
					text:'some internet issues with the server or in your side/if the message will fail, you will be informed.'
				})
				break;
			}
			// if got error\fai;ed message
			default:{
				Swal.fire({
					icon:'error',
					title:"Waiting for request answer",
					text:"Waiting for server give the data about the lock. Please press OK to retry",
					showCancelButton: true,
					confirmButtonColor: '#3085d6',
					cancelButtonColor: '#d33',
				}).then(result => {
					if(result.value){
						changeLockState(2);
						refreshButtonState()
					}
				});
				break;
			}

		}			
	})
});