/**
 * @auther Itamar Kanne
 * @file the main project file, includes all javascript code of the painter app
 */


/** @const FETCH_BOARD_INTERVAL */
const FETCH_BOARD_INTERVAL = 2000;

/** @const BACKGROUND_COLOR */
const BACKGROUND_COLOR = '#777777'

/**  @const CANVAS_SIZE size of the canvas */
const CANVAS_SIZE = 1000;

/** @const MIN_SCALE minimum scale power limit */
const MIN_SCALE = 0.5;

/** @const MAX_SCALE minimum scale power limit */
const MAX_SCALE = 50;

/**
 *  modules used in app
 *  {SocketIO} io io module, for talking with server
 *  {SweetAlert} Swal alert 
 *  {Underscore} _ module contains utilities functions
 *  {ClipboardJS} ClipboardJS module to work clipboard, copying and pasting data (url)
 * 
 */

// default cooldown between drawss
const DRAW_COOLDOWN = 60;

/** @const {number} PROGRESS_COOLDWN interval of time between each check to update the progress*/
const PROGRESS_COOLDOWN = 100;

/** @const {RegExp} reHashX  Hash x regex, used to find the x arg in the hash argument of the url*/
const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;

/** @const {RegExp} reHashY  Hash y regex, used to find the y arg in the hash argument of the url*/
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;

/** @const {RegExp} reHashScale  Hash scale regex, used to find the scale arg in the hash argument of the url */
const reHashScale = /(?<=(^#|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;

/** @const {RegExp} reHashX  Hash x regex, used to find the x arg in the hash argument of the url*/
const reArgX = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;

/** @const {RegExp} reHashY  Arg y regex, used to find the y arg in the arguments of the url*/
const reArgY = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;

/** @const {RegExp} reHashScale  Arg scale regex, used to find the scale arg in the arguments of the url */
const reArgScale = /(?<=(^\?|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;

/** @const {number} ZOOMED_IN_DEFAULT_LEVEL the default big zoom level */
const ZOOMED_IN_DEFAULT_LEVEL = 40;

/** @const {number} ZOOMED_OUT_DEFAULT_LEVEL the default small zoom level */
const ZOOMED_OUT_DEFAULT_LEVEL = 4;

/** @const {number} DEFAULT_START_AXIS the center of the board 500, where starting if no other arguments are found {@link mapFrags} */
const DEFAULT_START_AXIS = 500;

/** @const {socketIO} sock socket.io object to talk with the server */
const sock = io('/paint', {
	autoConnect: false,
	transports: ['websocket'] // or [ 'websocket', 'polling' ], which is the same thing
});

/**
 * wrapper function to reconnect using io, to only run it 5 seconds after sock.io run it
 */
const try_reconnect = _.throttle(() => sock.try_reconnect(), 5000, {leading: false, trailing:false})

/**
 * @template T
 * @param {T[]} group group of objects
 * @returns {?T} first item or null
 * returns returns first item in group, if cant returns null
 */
const getFirstIfAny = (group) => !group ? null : group[0]

/**
 * @param {number} v value
 * @param {number} max maximum value
 * @param {number} min minimum value
 * @returns {number} v if is in the range of min and max, 
 * otherwise returns min if the number if lower then min else max (higher then max)
 */
const clamp = (v, max, min) => Math.max(min, Math.min(v, max));

/**
 * 
 * @param {number} scale 
 * @returns {boolean} if valid scale
 */
const isValidScale = scale => MIN_SCALE <= scale && scale <= MAX_SCALE;

/**
 * 
 * @param {number} v an axis position
 * @returns {boolean} if the position is valid (x or y)
 * max CANVAS_SIZE, min limit 0
 */
const isValidPos = v => 0 <= v && v < CANVAS_SIZE;

/**
 * 
 * @param {*} num value suppose to be index of a Palette color (look down)
 * @returns {boolean} if its a valid color index
 * between(0, 16) include and in number
 */
const isValidColor = num => typeof num == 'number' && num >= 0 && num < 16
/**
 * @returns {boolean} if there any sweet alerts messages open
 */
const isSwalClose = () => _.isUndefined($('.swal2-container')[0])

/**
 * @returns {number} time in UTC
 * get current UTC time
 */
const getUTCTimestamp = () => {
	let tm = new Date();
	return Date.UTC(
		tm.getUTCFullYear(),
		tm.getUTCMonth(),
		tm.getUTCDate(),
		tm.getUTCHours(),
		tm.getUTCMinutes(),
		tm.getUTCSeconds(),
		tm.getUTCMilliseconds()
	)
}

/**
 * @returns {?number} map frag val or null
 * get a map pos value from regex check
 */
const getMapPos = _.compose(
	parseInt, 
	getFirstIfAny
)

/**

 * @returns {?number} map frag val or null
 * get a map scale value from regex check
 */
const getMapScale = _.compose(
	parseFloat, getFirstIfAny
)


/* View in fullscreen */
/**
 * open full screen
 * https://www.w3schools.com/howto/howto_js_fullscreen.asp
 */
function openFullscreen() {
	let elem = document.documentElement;
	if (elem.requestFullscreen) {
		elem.requestFullscreen();
	}
	//@ts-ignore
	else if (elem.mozRequestFullScreen) {
		/* Firefox */
		//@ts-ignore
		elem.mozRequestFullScreen();
	}
	//@ts-ignore
	else if (elem.webkitRequestFullscreen) {
		/* Chrome, Safari and Opera */
		//@ts-ignore
		elem.webkitRequestFullscreen();
	}
	//@ts-ignore
	else if (elem.msRequestFullscreen) {
		/* IE/Edge */
		//@ts-ignore
		elem.msRequestFullscreen();
	}
}
/**
 * close full screen (use also for non support)
 * @see {@link https://www.w3schools.com/howto/howto_js_fullscreen.asp}
 */
 function CloseFullscreen() {
	if (document.exitFullscreen) {
		document.exitFullscreen();
	}
	//@ts-ignore
	else if (document.mozCancelFullScreen) {
		/* Firefox */
		//@ts-ignore
		document.mozCancelFullScreen();
	}
	//@ts-ignore
	else if (document.webkitExitFullscreen) {
		/* Chrome, Safari and Opera */
		//@ts-ignore
		document.webkitExitFullscreen();
	}
	//@ts-ignore
	else if (document.msExitFullscreen) {
		/* IE/Edge */
		//@ts-ignore
	   document.msExitFullscreen();
	}
}

/**
 * @param {string} selector $(selector) matched string, specific the id of the clicked object
 * @returns null
 * if there are no alerts by the sweetalert extension open, the command executes clicking on a selector
 * is used for key events
 */
function nonSweetClick(selector) {
	if (isSwalClose()) {
		$(selector).click()
	}
}
/**
 * @param {string} msg message to display
 * @param {number} enter_sec the number of seconds take until starts to disappear from the moment fully appears 
 * @param {number} show_sec the number of seconds until fully shows
 * @param {?number} exit_sec the number of seconds before disappear
 * @param {string} cls the classes the message is member of
 * @returns throws a message to the user that doesn't blocks input
 */
const throw_message = (msg, enter_sec = 1000, show_sec = 100, exit_sec = 1000, cls = null) => {
	let popup = $("<div></div>").addClass(`pop-up-message center nonselect${_.isString(cls) ? ' ' + cls : ''}`).text(msg).appendTo("body")
	// enter
	popup.animate({opacity: '70%'}, enter_sec, function() {
		// keep the element amount of time
		setTimeout(function() {
				exit_sec = isNaN(exit_sec) ? enter_sec : exit_sec;
				if (exit_sec > 0) {
					$(popup).animate({
							opacity: '0'
						},
						exit_sec,
						function() {
							// remove self
							$(this).remove();
						});
				} else {
					$(popup).remove();
				}
			},
			show_sec
		);
	});
}


/**
 * @property {Vector2D} direction a vector repressing the normal of the direction to move while key is pressed
 * @property {boolean} if key is pressed
 * @desc class to use with direction map
 * @see {@link:DirectionMap}
 */
class KeyDirection {
    /**
     * @param {Vector2D} direction the direction
     */
    constructor(direction) {
        this.direction = direction;
        this._is_set = false;
    }
	/**
	 * clears the _is_set property, if the property was set
	 * @returns {boolean} if this._is_set value was true before the function
	 */
	clearIfSet(){
		if(this._is_set){
			this._is_set = false;
			return true;
		}
		return false;
	}
	/**
	 * sets the _is_set property, if the property was cleared
	 * @returns {boolean} if this._is_set value was false before the function
	 */
	setIfCleared(){
		if(!this._is_set){
			this._is_set = true;
			return true;
		}
		return false;
	}
}


/**
 * @enum {KeyDirection}
 * an object using to determine changing of movement direction with the key mode
 * @see {@link board.Movement}
*/
const DirectionMap = {
	ArrowLeft: new KeyDirection(new Vector2D(-1, 0)),
	ArrowRight: new KeyDirection(new Vector2D(1, 0)),
	ArrowUp: new KeyDirection(new Vector2D(0, -1)),
	ArrowDown: new KeyDirection(new Vector2D(0, 1))
}


/**
 * @class
 * @property {function} work
 * @desc
 * SimpleInterval is a class that represent a "worker" which
 * executes a function each X time
 * the function uses the Interval API
 * @see {@link https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/setInterval}
 */
class SimpleInterval {
    /**
     * @name _work_handler
     * @type {number} 
     * @desc created by the constructor, default null. the handler for the setInterval
     */
	/**
	 * @param {function} work function to run each 
	 * @param {number} time the time between each call
	 */
	constructor(work, time) { 
		this._work = work;
		this._time = time;
		this._work_handler = null;
	}
	/**
	 * @desc start the worker
	 */
	start() {
		this._work_handler = setInterval(this._work, this._time);
	}
	/**
	 * @desc stops the worker
	 */
	stop() {
		clearInterval(this._work_handler)
		this._work_handler = null
	}
	/**
	 * @returns if the worker starts to work (and hasn't already worked)
	 * @desc safely starts the worker, only if the worker isn't already working
	 */
	safeStart() {
		if (this.isWorking) {
			return false;
		}
		this.start()
		return true;
	}
	/**
	 * @returns {boolean} if the worker stopped
	 * stops starts the worker, only if the worker isn't already working
	 */
	safeStop() {
		if (!this.isWorking) {
			return false
		} //else 
		this.stop();
		return true;
	}
	/**
	 * checks if the worker is working at all using the handler
	 */
	get isWorking() {
		return !_.isNull(this._work_handler);
	}
}

/**
 * @desc represents state of cursor, if to show the colored pixel that is how the pen is made or not 
 * and the values
 */
class CursorState {
	/**
	 * @param {string} cursor the cursor text to set the css cursor attribute
	 * @param {boolean} hide_pen if to hide the pen color on the board
	 */
	constructor(cursor, hide_pen) {
		this.cursor = cursor;
		this.hide_pen = hide_pen;
	}
	/**
	 * @param {?CursorState} other_cursor other cursor object mayby
	 * @returns boolean -> if the 2 cursors states are the same
	 * @desc checks if the curser equals to the other object
	 */
	equals(other_cursor) {
		//https://stackoverflow.com/a/1249554
		if (!(other_cursor instanceof CursorState)) {
			return false;
		}
		return this.cursor == other_cursor.cursor && this.hide_pen == other_cursor.hide_pen
	}
}


/**
 * @const Cursors
 * @desc contains the possible cursors uses the CursorState
 * @enum {CursorState}
 */
const Cursors = {
	pen: new CursorState('crosshair', false),
	wait: new CursorState('wait', true),
	grabbing: new CursorState('grabbing', true),
}

/**
 * @property {number} red red value of the color in rgb
 * @property {number} green green value of the color in rgb
 * @property {number} blue blue value of the color in rgb
 * @property {name} name of the color
 * @desc simple class to represent colors the can be placed on the board, the colors are saved as in RGB format
 */
class Color {
	/**
	 * @param {number} red the r value
	 * @param {number} green the green value
	 * @param {number} blue blue value of the color in rgb
	 * @param {string} name name of the color
	 * @returns new Color object
	 * @desc basic paramter-value constructor
	 */
	constructor(red, green, blue, name) {
		this.red = red;
		this.green = green;
		this.blue = blue;
		this.name = name;
	}
	/**
	 * @returns {number} abgr values
	 * calculates abgr value
	 * caluclates abgr value of color, opposite order to rgba because bit position
	 */
	getAbgr() {
		return (0xFF000000 | this.red | this.green << 8 | this.blue << 16) << 0;
	}
	/**
	 * @param {number} alpha alpha value in real number percent ratio 
	 * @returns {string} text equals to rgba function of css of the color with the passed alpha value
	 */
	css_format(alpha = 1) {
		return `rgba(${this.red}, ${this.green}, ${this.blue}, ${alpha})`;
	}
}


/**
 * @const colors 
 * @desc an object holding the colors and handling interactions with them
 * @enum {Color}
 */
const colors = [
	new Color(0xFF, 0xFF, 0xFF, 'White'),
	new Color(0x00, 0x00, 0x00, 'Black'),
	new Color(0x80, 0x80, 0x80, 'Gray'),
	new Color(0xC0, 0xC0, 0xC0, 'Silver'),
	new Color(0xFF, 0x00, 0x00, 'Red'),
	new Color(0xFF, 0xC0, 0xCB, 'Pink'),
	new Color(0x8B, 0x45, 0x13, 'Brown'),
	new Color(0xFF, 0xA5, 0x00, 'Orange'),
	new Color(0x80, 0x80, 0x00, 'Olive'),
	new Color(0xFF, 0xFF, 0x00, 'Yellow'),
	new Color(0x00, 0x80, 0x00, 'Green'),
	new Color(0x00, 0xFF, 0x00, 'Lime'),
	new Color(0x00, 0x00, 0xFF, 'Blue'),
	new Color(0x00, 0xFF, 0xFF, 'Aqua'),
	new Color(0x80, 0x00, 0x80, 'Purple'),
	new Color(0xFF, 0x00, 0xFF, 'Magenta')
]


/**
 * @namespace
 * @desc progress object handles all related staff to the progress bar on the screen
 */
const progress = {
	/**
	 * @name when_cooldown_ends
	 * @type {number}
     * @memberof progress
	 * @desc time of the progress
	 */
	when_cooldown_ends: 0,
	/**
	 * @name state
	 * @type {number}
     * @memberof progress
     * @desc the state of the progress (0-2), 0-stopped, 1-start wait 2-half time passed
	 */
	state: 0,
	/**
	 * @name _work
	 * @type {SimpleInterval}
	 * @desc SimpleInterval for updating auto update the progress bar.  handler of progress update interval
	 */
	_work: null,
	/**
	 * @name _current_seconds
	 * @type {string}
     * @memberof progress
	 * @desc to make progress text update event 1 seconds
	 */
	_current_seconds: null,
	/**
     * @desc constructor, the object initialization sets his work
	 */
	preRun() {
        // bind the timer to itself
        let bind_timer = _.bind(
            this.updateTimer,
            this
        )
		this._work = new SimpleInterval(bind_timer, PROGRESS_COOLDOWN)
	},
	/**
     * @returns {boolean} if progress still works
     * @desc if progress isn't finished, user still cant place pixels
     */
	isWorking(){
		return this._work.isWorking;
	},
	/**
	 * @param {number} seconds_left number of seconds before the progress bar ends
	 * @desc update the progress bar text and state
	 */
	adjustProgress(seconds_left) {
		// adjust the progress bar and time display by the number of seconds left
		$('#prog-text').text([
			(Math.floor(seconds_left / 60)).toString(),
			(seconds_left % 60).toString().padStart(2, '0')
		].join(':'))
		// update progress fill
		// update area colored
		$('#prog-fill').css('width', (100 - (seconds_left / DRAW_COOLDOWN) * 100).toString() + "%");
		// 1 if time less then halve the number of seconds 
		this.state = Math.ceil(seconds_left * 2 / DRAW_COOLDOWN);
		$('#time-prog').attr('state', this.state);
	},
	/**
	 * @param {string} time when the date finishes 
	 * @desc set the time for the progress and start working
	 */
	setTime(time) {
		// handles starting the timer waiting
		console.log(time)
		this.when_cooldown_ends = Date.parse(time + ' UTC');
		// if current time is after end of cooldown
		if (this.when_cooldown_ends < getUTCTimestamp()) {
			$('prog-text').text('0:00'); // set text 0
			$('#prog-fill').attr('state', 1); // prog-fill state is 9
			$('#time-prog').attr('state', 0); // time progress set to 1
			this._work.safeStop()
		}
		// when stops working
		else if (!this.isWorking()) {
			// to be changeable
			this._current_second = -1;
			this._work.start()
			// set cursor to be pen
			cursor.setPen();
		}
	},
	/**
     * @desc
	 * the function the worker runs, to update every x milliseconds the progress bar dom object
	 * Updates the progress bar and timer each interval
	 * Math.max the time until cooldown ends in ms, compare if positive (the time has not passed),
     * ceil to round up, I want to prevent the progress showing time up to that
	 */
	updateTimer() {
		let seconds_left = Math.ceil(Math.max(this.when_cooldown_ends - getUTCTimestamp(), 0) / 1000);
		// adjust progress
		if (this._current_second != seconds_left) {
			this.adjustProgress(seconds_left);
			// update current time
			this._current_second = seconds_left;
		}
		// close for cooldown 0
		if (seconds_left <= 0) {
			// clear Interval
			this.stopProgress();
		}
	},
	/**
	 * @desc stops the progress bar
	 */
	stopProgress() {
		this._work.stop();
		cursor.setPen();
	}
}

/**
 * @namespace
 * @desc handles working with the url and movement of the board
 */
const mapFrags = {
    /**
	 * @name cx
     * @memberof mapFrags
	 * @type {number}
	 * @desc the x position of the pixel at the center of the screen
	 */
	cx: DEFAULT_START_AXIS,
	/**
	 * @name cy
     * @memberof mapFrags
	 * @type {number}
	 * @desc the y position of the pixel at the center of the screen
	 */
	cy: DEFAULT_START_AXIS,
	/**
	 * @name scale
     * @memberof mapFrags
	 * @type {number}
	 * @desc the amount of zoom on the screen
	 */
	scale: ZOOMED_OUT_DEFAULT_LEVEL,
	/**
	 * @method
     * @name fixHash
     * @memberof mapFrags
     * @desc
     * wraps _fixHash function with _.throttle function
	 * throttle executes the function once every x time, and if the function was called during the waited time,
	 * it executes it when the time ends.
	 * @see {@link https://underscorejs.org/#throttle}
	 */
	fixHash: null,
	/**
     * @function
	 * initialize the object, all related document function, runs when document is ready
	 */
	preRun() {
		// set window hash to be valid
		this.fixHash = _.throttle(this._fixHash, 1000);
		let fragments = this._determineFragments();
		this.cx = fragments.x;
		this.cy = fragments.y;
		this.scale = fragments.scale;
	},

	doesHashMatch(){
		return mapFrags.hash() != window.location.hash;
	},
	/**
	 * calculates size of step, used for other functions
     * == 50/this.scale
	 * @returns {number} size of step (amount of window pixels that fit 1 board pixel) in pixels
	 */
	getStepSize() {
		return MAX_SCALE / mapFrags.scale;
	},
	/**
	 * @private
	 * @returns {string} the raw path for the map
	 */
	_getFragsAsPathParams() {
		return `x=${this.cx}&y=${this.cy}&scale=${this.scale}`
	},
	/**
	 * @returns {string} hash params of the url with the same map position
	 */	hash() {
		return `#${this._getFragsAsPathParams()}`
	},
	/**
	 * @returns {string} arguments param of the url with the same map position
	 * the value for location's hash field to set mapFrags as current
     * @summary simple get
	 */
	asArgument() {
		return `?${this._getFragsAsPathParams}`
	},
	/**
	 * @param {Vector2D} vector represent the new center
	 * center the board at the vector (represents a point)
	 */
	centerOn(vector){
		x = isNaN(vector.x) ? mapFrags.cx : clamp(vector.x, CANVAS_SIZE, 0);
		y = isNaN(vector.y) ? mapFrags.cy : clamp(vector.y, CANVAS_SIZE, 0);
		this.setCenter(vector.x, vector.y);
	},
	/**
	 * @param {number} val 
	 * @returns {boolean} if the value can be the next cx value (next value means its different from current)
	 * if value is valid 'new' center x
	 */
	_isValidNewX(new_x) {
		return (!isNaN(new_x)) && isValidPos(new_x) && new_x != this.cx
	},
	/**
	 * @param {number} new_y 
	 * @returns {boolean} if the param can be the next cy value (next value means its different from current)
	 * if value is valid 'new' center y
	 */
	_isValidNewY(new_y) {
		return (!isNaN(new_y)) && isValidPos(new_y) && new_y != this.cy
	},
	/**
	 * @param {number} new_scale 
	 * @returns {boolean} if the param can be the next cy value (next value means its different from current)
	 * if value is valid 'new' scale
	 */
	_isValidNewScale(new_scale) {
		return (!isNaN(new_scale)) && isValidScale(new_scale) && new_scale != this.scale
	},
	/**
	 * @returns the x position the board suppose to be on the screen.
	 * the function first check by the arguments, then by the hash and finally by the favorable position
	 * determine x locaiton by checking fields
	 * first check the arguments
	 * then checks the hash
	 * after the current center x
	 * then checks for default
	 * and in the end, returnd default DEFAULT_CENTER_AXIS (500)
	 */
	_determineX() {
		// first get from arguments
		let x = getMapPos(window.location.search.match(reArgX));
		if ((!isNaN(x)) && isValidPos(x)) {
			return x;
		}
		// second get from hash
		x = getMapPos(window.location.hash.match(reHashX));
		if ((!isNaN(x)) && isValidPos(x)) {
			return x;
		}
		// else search for value in body
		x = parseInt($('body').attr('x'))
		if ((!isNaN(x)) && isValidPos(x)) {
			return x;
		}
		if(_.isNumber(this.cx)){
			return this.cx;
		}
		return DEFAULT_START_AXIS;
	},
	/**
	 * @returns the y position the board suppose to be on the screen.
	 * the function first check by the arguments, then by the hash and finally by the favorable position
	 * determine scale value by checking fields
	 * first the arguments
	 * then checks the hash
	 * after the current scale (this.scale)
	 * then checks for default
	 * and in the end, returned default zoom level (4)	 */
	_determineY() {
		// first get from arguments
		let y = getMapPos(window.location.search.match(reArgY));
		if ((!isNaN(y)) && isValidPos(y)) {
			return y;
		}
		// second get from hash
		y = getMapPos(window.location.hash.match(reHashY));
		if ((!isNaN(y)) && isValidPos(y)) {
			return y;
		}
		// else search for value in body
		y = parseInt($('body').attr('y'))
		if ((!isNaN(y)) && isValidPos(y)) {
			return y;
		}
		if(_.isNumber(this.cy)){
			return this.cy;
		}
		return DEFAULT_START_AXIS;
	},
	/**
	 * @returns the y position the board suppose to be on the screen.
	 * @desc the function first check by the arguments, then by the hash and finally by the favorable position
	 */
	_determineScale() {
		let scale = getMapScale(window.location.search.match(reArgScale));
		if ((!isNaN(scale)) && isValidScale(scale)) {
			return scale;
		}
		// second get from hash
		scale = getMapScale(window.location.hash.match(reHashScale))
		if ((!isNaN(scale)) && isValidScale(scale)) {
			return scale;
		}
		// else search for value in body
		scale = parseFloat($('body').attr('scale'))
		if ((!isNaN(scale)) && isValidScale(scale)) {
			return scale;
		}
		if(_.isNumber(this.scale)){
			return this.scale;
		}
		return ZOOMED_OUT_DEFAULT_LEVEL;
	},
	moveBoard(dx, dy) {
		mapFrags.setCenter(
			clamp(mapFrags.cx + dx * this.getStepSize(), CANVAS_SIZE, 0),
			clamp(mapFrags.cy + dy * this.getStepSize(), CANVAS_SIZE, 0)
		);
	},
	/**
	 * @returns the fields of the object
	 * @desc determine the current fragments and update board
	 */
	_determineFragments() {
		return {
			x: this._determineX(),
			y: this._determineY(),
			scale: this._determineScale()
		};
	},
	/**
	 * @param {number} x new x position of the center of the viewport
	 * @param {number} y new y position of the center of the viewport
	 * @param {boolean} to_update if to update the position, used when using the function with the setScale method
	 * @returns {boolean} if the cx or cy fragments have been changed
	 * @desc handles setting the new center, also prevent any changes if the scale level is less then 1 (0.5)
	 */
	setCenter(x = undefined, y = undefined, to_update = true) {
		let flag = false;
		// if any undefined it returns NaN
		x = this.scale >= 1 ? Math.round(x) : CANVAS_SIZE / 2;
		y = this.scale >= 1 ? Math.round(y) : CANVAS_SIZE / 2;
		if (this._isValidNewX(x)) {
			flag = true;
			this.cx = x;
		}
		if (this._isValidNewY(y)) {
			flag = true;
			this.cy = y;
		}
		if (to_update && flag) {
			board.centerPos(this.cx, this.cy);
			this.fixHash();
		}
		return flag;
	},
	/**
	 * @param {number} scale the new scale value to view the page
	 * @param {boolean} to_update if to update the
	 * @desc if the scale level is less then 0.5
	 */
	setScale(scale, to_update = true) {
		if (this._isValidNewScale(scale)) {
			this.scale = scale;
			if (1 > this.scale) {
				this.setCenter(CANVAS_SIZE / 2, CANVAS_SIZE / 2, false);
			}
			if (to_update) {
				// update board
				board.updateZoom();
			}
			this.fixHash()
		}
	},
	/**
	 * @returns if any changes to the view
	 * @desc refreshes the page position variables and fixes them
	 */
	refreshFragments() {
		let frags = this._determineFragments();
		let any_changes = frags.x != this.cx || frags.y != this.cy || frags.scale != this.scale;
		if(any_changes){
			this.setCenter(frags.x, frags.y, this._isValidNewScale(frags.scale));
			if (this._isValidNewScale(frags.scale)) {
				this.scale = frags.scale;
				board.updateZoom();
			}
		}
		return any_changes;
		
	},
	/**
	 * function handling fixing the hash displayed
	 * another function wraps it to make it only be only x time after the last the function was called
	 */
	_fixHash() {
		//  update location
		// first tried to update event set
		// now lets try using setTimeout
		if (this.doesHashMatch()) {
			// change hash without triggering events
			/** @link https://stackoverflow.com/a/5414951 */
			location.replace(this.hash())
		}
	},
	/**
	 * sets the hash on first time
	 * includes the arguments function (if it has)
	 */
	fixLocation(){
		if (this.doesHashMatch()) {
			history.replaceState(null, null, document.location.pathname + this.hash());
		}
	},
	/**
	 * sets the style of the zoom button depending the zoom level on the scale
	 */
	refreshZoomStyle() {
		let zoom_button = $('#zoom-button')
		if (this.scale >= 25) {
			zoom_button.children('span').addClass('fa-search-minus').removeClass('fa-search-plus');
			zoom_button.css('cursor', 'zoom-out');
		}
		else {
			zoom_button.children('span').addClass('fa-search-plus').removeClass('fa-search-minus');
			zoom_button.css('cursor', 'zoom-in');
		}
	},
}

/** 
 * @namespace
 * @property {?CursorState} current_cursor  current cursor object represent the cursor state
 * @property {?CursorState} force_cursor option to force the current cursor to specific object
 * @property {?CursorState} last_cursor_non_forced the last cursor that wasnt forced
*/
const cursor = {
	last_cursor_non_forced: null,
	current_cursor: null,
	force_cursor: null,
	/**
	 * @param {?CursorState} other_cursor cursor set (if cursor isnt forced)
	 * sets the new cursor
	 */
	updateCursor(other_cursor=null) {
		// update last cursor
		// check if setting any cursor
		if (other_cursor instanceof CursorState) {
			this.last_cursor_non_forced = other_cursor;
		}
		// if has any forced cursor pick him, else pick the last non forced cursor
		let cursor = this.force_cursor || this.last_cursor_non_forced;
		//  if new current_cursor is different
		if (_.isNull(this.current_cursor) || !this.current_cursor.equals(cursor)) {
			this.refreshCursor(cursor)
		}
	},
	/**
	 * 
	 * @param {CursorState} cursor_state new cursor state
	 * updates the cursor state
	 */
	refreshCursor(cursor_state){
		// sets
		if ((!this.current_cursor) || cursor_state.cursor != this.current_cursor.cursor) {
			board.canvas.css('cursor', cursor_state.cursor);
		}
		if (cursor_state.hide_pen) {
			pen.disable();
		}
		else {
			pen.enable();
		}
		this.current_cursor = cursor_state;
	},
	/**
	 * sets the cursor to pen or wait state, depending if the progress bar is waiting
	 */
	setPen() {
		this.updateCursor(progress.isWorking() || lockedState.locked ? Cursors.wait : Cursors.pen)
	},
	/**
	 * sets the cursor state to grab state
	 */
	grab() {
		this.updateCursor(Cursors.grabbing);
	},
	/**
	 * @param {CursorState} cursor_state the cursor state to lock the pen
	 * locks a specific cursor state on pen
	 */
	lockCursor(cursor_state) {
		this.force_cursor = cursor_state;
		this.updateCursor();
	},
	/**
	 * @param {CursorState} cursor_state the cursor_state the if the pen is forced to it,is freed from it
	 * releases the cursor and updates cursor if the cursor_state is the current one that is locked
	 */
	releaseCursor(cursor_state) {
		if (cursor_state.equals(this.force_cursor)) {
			this.force_cursor = null;
			this.updateCursor()
		}
	}
}


/**
 * @property {Vector2D} start_vector a vector holding the center xy of the board when start dragging
 * @property {Vector2D} drag_vector a vector holding the position of the mouse relative to the canvas element when grabed it
 * @desc DragData constructor, object representing the information the board being dragged
 */
class DragData {
    /**
     * @param {number} start_x where started to drag (in x axis, measure by board pixels)
     * @param {number} start_y where started to drag (in y axis, measure by board pixels)
     * @param {number} drag_x  where the mouse press (in x axis, measure by screen pixels)
     * @param {number} drag_Y  where the mouse press (in y axis, measure by screen pixels)
     */
	constructor(start_x, start_y, drag_x, drag_y){
		this.start_vector = new Vector2D(start_x, start_y);
		this.drag_vector = new Vector2D(drag_x, drag_y)
	}
	/**
	 * @method
	 * @param {Vector2D} new_pos mouse event to check the new position of the mouse
	 * @param {number} scale scale multiplayer
	 * @returns {Vector2D} vector2d represent the position an object is dragged to
	 */
	getDraggedPos(new_pos, scale){
		let dragged_position = this.drag_vector.clone().subVector(new_pos).divXY(scale);
		let v=new Vector2D(
			Math.floor(dragged_position.x) + this.start_vector.x,
			Math.floor(dragged_position.y) + this.start_vector.y
		)	 
		return v;
	}
}

/** @namespace */
const pen = {
	/**
	 * @name x
     * @memberof pen
	 * @type {number}
	 * @desc the x position the mouse points to (on the board else null)
	 */
	x: -1,
	/**
	 * @name y
     * @memberof pen
	 * @type {number}
	 * @desc the y position the mouse points to (on the board else null)
	 */
	y: -1,
	/**
	 * @name _color
     * @memberof pen
	 * @type {?number}
	 * @desc the color of the pen
	 */
	_color: null,
	/**
	 * @name last_mouse_pos
     * @memberof pen
	 * @type {number[]}
	 * @desc the (x,y) position the mouse moved to (if its on the board)
	 */
	last_mouse_pos: null,
	/**
	 * @name is_in_center_mode
     * @memberof pen
	 * @type {boolean}
	 * @desc if the pen is in center mode == key movement mode
	 */
	is_in_center_mode: true,
	/**
	 * @name _disable
     * @memberof pen
	 * @type {boolean}
	 * @desc if the pen is in disabled mode, invincible
	 */
	_disable: false,
	/**
	 * @name cursor_style
     * @memberof pen
	 * @type {string}
	 * @desc  the cursor style to put the mouse on
	 */
	cursor_style: 'default',
	/**
	 * @name drag_data
     * @memberof pen
	 * @type {DragData}
	 * @desc object represent the drag state of the board when dragged by the mouse (pen)
	 */
	drag_data: null,
	/**
	 * @returns {boolean} if pen drags the board
	 * @desc the board is being drag if pen has drag_data value
	 */
	isDragged(){
		return !_.isNull(this.drag_data)
	},
	/**
	 * @function
	 * @desc stop dragging the board
	 */
	stopDrag(){
		this.drag_data = null;
	},
	/**
     * @desc
	 * pre runs the pen object (just setting the color buttons, and set one of them to active),
	 * initilize the color
	 * this applys when the document is ready for javascript editing
	 */
	preRun() {
		let color_button = $('.colorButton[picked="1"]').first()
		if (!color_button[0]) {
			color_button = $('.colorButton').first(); // black button
		}
		this.setColorButton(color_button);
	},
	/**
     * @desc
	 * clears the canvas pen and updates the board
	 */
	disable() {
		// if not disabled don't do anything
		if (!this._disable) {
			this._disable = true;
			board.drawBoard();
		}
	},
	/**
	 * resets the canvas pen and updates the board
	 */
	enable() {
		if (this._disable) {
			this._disable = false;
			board.drawBoard();
		}
	},
	/**
     * @method
	 * @param {?jQuert.Event} e $ event that wraps a mouse event, if not restores from last one used
	 * the mouse position (if there is not event,resets then to last)
	 */
	getMouseOffset(e) {
		if (e) {
			// set last_mouse_pos
			this.last_mouse_pos = [e.pageX, e.pageY]
		}
		return this.last_mouse_pos;
	},
	/**
     * @method
	 * @param {?MouseEvent} e mouse event or null (if its in keyboard mode)
	 * @returns {number[]} position (x, y) 
	 */
	updateOffset(e=null) {
		/* finds the pen current position
		 min pixel on screen + start of page / scale= position of mouse  */
		let pos = null;
		if (this.is_in_center_mode) {
			pos = {
				x: Math.floor(board.x + board.canvas[0].width / 2 / mapFrags.scale),
				y: Math.floor(board.y + board.canvas[0].height / 2 / mapFrags.scale)
			} // center
		}
		else {
			// clear pos when both values aren't good
			let mouse_offset = this.getMouseOffset(e);
			if (_.isNull(mouse_offset) || _.some(mouse_offset, _.isNull)) {
				return;
			}
			pos = {
				x: Math.floor(board.x + mouse_offset[0] / mapFrags.scale),
				y: Math.floor(board.y + mouse_offset[1] / mapFrags.scale)
			}
		}
		if (_.isNull(pos) || (!isValidPos(pos.x)) || (!isValidPos(pos.y))) {
			this.clearPos(); // set values to -1
			// but if not, update if the values are different
		}
		else if (pos.x != this.x || pos.y != this.y) {
			this.x = pos.x;
			this.y = pos.y;
			board.drawBoard();
			board.updateCoords();
		}
	},
	/**
	 * clears the position the pen and set the board to update in next refreshAnimation loop
	 */
	clearPos() {
		// when out of board
		this.x = this.y = -1;
		board.updateCoords();
		board.drawBoard();
	},
	/**
	 * @param {jQuery.Event} e mouse event
	 * @desc updates the offset and stop the keyboard mode 
	 */
	setPenPos(e) {
		// update position and end use of keyboard state center
		this.is_in_center_mode = false;
		this.updateOffset(e);
	},
	/**
	 * set pen to center
	 */
	setCenterPos() {
		cursor.setPen();
		this.is_in_center_mode = true;
		this.updateOffset();
	},
	/**
	 * @param {jQuery} button 
	 * sets the color of the button as the pens color also set the button to focused (means thats the color of the pen)
	 */
	setColorButton(button) {
		this.color = parseInt(button.attr('value'));
		$('.colorButton[picked="1"]').attr('picked', '0');
		button.attr('picked', '1');
	},
	/**
     * @returns {boolean} if has color
     */
	hasColor() {
		return isValidColor(this._color);
	},
	/**
     * @returns {number} index of pen color 
	 * gets the color index value
	*/
	get color() {
		return this._color;
	},
	/**
	 * @param {number} value
	 * sets the color
	 */
	set color(value) {
		if (value >= 0 && value < 16 && this._color != value) {
			this._color = value;
			board.drawBoard()
		}
	},
	/**
	 * @returns {boolean} if mouse points to the board
	 */
	get isAtBoard() {
		return this.x != -1 || this.y != -1
	},
	/**
	 * @returns {boolean} if can draw pen
	 * can se pixel if pen isn't disabled, has color, is at board and board is ready (loaded data from server)
	 */
	canDrawPen() {
		return (!this._disable) && this.hasColor() && this.isAtBoard && board.is_ready;
	},
	/**
	 * <p>set a pixel on board (emits to server)</p>
	 * <p>raises error if socket io isn't connected, board isn't loaded, cooldown hasn't ended</p>
	 * <p>pen has no color, or some admin lock the users from changing the canvas</p>
	 * <p>the server returns a response in form {code:string, status:string}, </p>
	 * <p>if cooldown hasn't ended or reset gets code 'time' when the status stores when the cooldown ends</p>
	 * <p>if board is locked returns code:'lock' with status 'true''</p>
	 */
	setPixel() {
		if(!sock.connected) {
			Swal.fire({
				title: 'Server Not Found',
				imageHeight: 300,
				imageUrl:'https://i.chzbgr.com/full/570936064/hF75ECDD4/error-404-server-not-found',
				imageAlt:'Server Not Found and Also this image, maybe you out of numberernet',
				text:'The Server Cannot be Found, if you wait a little it might be found',
				confirmButtonText: 'Back to Wait'
			})
			// also again check with server if 5 seconds after didn't load
			try_reconnect()	
		}
		// if board isn't ready
		if (!board.is_ready) {
			Swal.fire({
				title: 'Wait for the board',
				text: 'Wait for the board to load before doing something'
			});
		}
		// progress working -> waits for the next time the player can draw
		else if (progress.isWorking()) {
			Swal.fire({
				title: 'You have 2 wait',
				imageUrl: 'https://aadityapurani.files.wordpress.com/2016/07/2.png',
				imageHeight: 300,
				imageAlt: 'wow that was rude',
				text: 'Wait for your cooldown to end'
			});
		}
		// if locked
		else if (lockedState.locked) {
			Swal.fire({
				title: 'Canvas is closed',
				imageUrl: 'https://img.memecdn.com/door-lock_o_2688511.jpg',
				imageHeight: 250,
				imageAlt: 'Social Painter Dash canvas is currently locked',
				text: 'Wait an admin will open it up',
				confirmButtonText: 'To Waiting'
			});
		}
		else if (!this.hasColor()) {
			Swal.fire({
				icon: 'warning',
				title: 'Select Color',
				text: 'pless select color from the table',
			});
		}
		else {
			sock.emit('set-board', {
				'color': this._color,
				'x': this.x,
				'y': this.y,
			}, (value) => {
				if (_.isUndefined(value) || value == 'undefined') {
					return;
				}
				// else it must be json
				let data = JSON.parse(value);
				if(_.isNull(data)){
					Swal.fire({
						icon:'danger',
						title:'Error',
						text:'You need to wait a couple of seconds between each set'
					})
				}
				switch(data.code){
					case 'lock': {
						if(data.status == 'true'){
							lockedState.lock()
						}
						break;
					}	
					case 'time': {
						progress.setTime(data.status)
						break;
					}
					default: {
						// simple break
						break;
					}
				}
			});
		}
	}
}


/** 
 * @namespace 
 * @type {Object.<string, any>}
 * @desc object to work with the board
 */
const board = {
	/**
	 * @name img_canvas
     * @memberof board
	 * @type {HTMLCanvasElement}
	 * @desc canvas to save the entire image of the canvas
	 */
	img_canvas: null,
	/**
	 * @name x
     * @memberof board
	 * @type {number}
	 * @desc space between head of the board to the x start of the page
	 */
	x: 0,
	/**
	 * @name y
     * @memberof board
	 * @type {number}
	 * @desc space between head of the board to the x start of the page
	 */
	y: 0,
	/**
	 * @name canvas
     * @memberof board
	 * @type {?jQuery}
	 * @desc the canvas displayed to the user in jquery
	 */
	canvas: null,
	/**
	 * @name needs_draw
     * @memberof board
	 * @type {boolean}
	 * @desc if hasn't called for the draw method
	 */
	needs_draw: false,
	/**
	 * @name move_vector
     * @memberof board
	 * @type {Vector2D}
	 * @desc vector to use for the key_move_work
	 */
	move_vector: Vector2D.zero(),
	/**
	 * @name key_move_work
     * @memberof board
	 * @type {?SimpleInterval}
	 * @desc the work which handles continuously moving the board by keys
	 */
	key_move_work: null,
	/**
	 * @name pixelQueue
     * @memberof board
	 * @type {Array.<Object.<string, number>>}
	 * @desc queue of pixel to draw
	 */
	pixelQueue: [],
	/**
     * @method
	 * @name buildBoard
     * @memberof board
	 * @type {function}
	 * @desc wraps the buildBoard to only do it once, when get the data, to prevent 2 recalls
	 */
	buildBoard: null,
	/**
	 * @name is_ready
     * @memberof board
	 * @type {boolean}
	 * @desc if ready to the display board, after the board was load
	 */
    is_ready: false,
	/**
	 * preRun operation
	 * adds HTML elements
	 * created the move board work
	 * sets the build board function
	 * also uses the updateZoom method to set the position
	 */
	preRun() {
		this.buildBoard = _.once(this._buildBoard);
		this.canvas = $('#board');
		this.img_canvas = document.createElement('canvas');
		this.img_canvas.width = CANVAS_SIZE;
		this.img_canvas.height = CANVAS_SIZE;
		// bind the function to this object
		let bind_move_board = _.bind(
			 () => mapFrags.moveBoard(
				 this.move_vector.x,
				 this.move_vector.y
				),
			 this
		)
		// creates the work
		this.key_move_work = new SimpleInterval(
			bind_move_board, 100
		)
		this.updateZoom(); // also centers and adjust for devicePixelRatio
	},
	/**
	 * simple get
	 * @returns {CanvasRenderingContext2D} the context of the displayed board
	 */
	getCanvasContext(){
		return this.canvas[0].getContext('2d');
	},
	/**
	 * returns the context of the display board
	 * @returns {CanvasRenderingContext2D} the context of the canvas that contains the full board
	 */
	getImageContext(){
		return this.img_canvas.getContext('2d');
	},
	/**
	 * resets board build by setting the buildBoard method is_ready to false
	 */
	resetBoardBuild() {
		this.buildBoard = _.once(this._buildBoard);
		board.is_ready = false
	},
	/**
	 * adds the vector to the move vector property
	 * also starts moving the board if didnt work
	 * @param {Vector2D} dir direction to move the board
	 */
	addMovement(dir) {
		this.move_vector.addVector(dir);
		mapFrags.moveBoard(dir.x, dir.y)
		this.key_move_work.safeStart();
	},
	/**
	 * @param {Vector2D} dir direction vector to subtract from the subMovement method
	 * subtracts from the movement vectors
	 */
	subMovement(dir) {
		this.move_vector.subVector(dir);
		if (this.move_vector.isZero()) {
			this.key_move_work.safeStop();
		}
	},
	/**
	 * builds the board first time
	 * @param {Uint8Array} buffer buffer of bytes represent the board
	 */
	_buildBoard(buffer) {
		// creates new image to display
		let image_data = new ImageData(CANVAS_SIZE, CANVAS_SIZE);
		// loads the buffers of the image data
		let image_buffer = new Uint32Array(image_data.data.buffer);
		buffer.forEach(function(val, index) {
			// first version of putting data, looping over the image buffer array and not of buffer of message
			//var bit = buffer[Math.floor(index/2)];
			//self.buffer[index] = reverseRGBA(COLORS[index % 2 == 0 ? bit % 16 : bit >> 4]);
			image_buffer[index * 2] = colors[val % 16].getAbgr(); // small number
			image_buffer[index * 2 + 1] = colors[Math.floor(val / 16)].getAbgr(); // big number
		});
		this.getImageContext().putImageData(image_data, 0, 0);
		// load pixel queue
		this.loadPixelQueue();
	},
	/**
	 * 
	 * @param {number} x x position of pixel 
	 * @param {number} y position of pixel
	 * @param {string} color color to draw the pixel
	 */
	_setAt(x, y, color) {
		let image_context = this.getImageContext()
		// set pixel color
		image_context.fillStyle = color;
		// fills the pixel
		image_context.fillRect(x, y, 1, 1);
		// redraw board
		this.drawBoard();
	},
	/**
	 * 
	 * @param {*} x position of the pixel 
	 * @param {*} y position of the pixel
	 * @param {*} color_idx index of the color
	 * validates a values
	 */
	setAt(x, y, color_idx) {
		// set a pixel at a position
		// x: number (0 < x < 1000)
		// y: number (0 < x < 1000)
		if (!isValidColor(color_idx)) {
			// swal event
			throw_message('the server/you (if you trying) are trying to set a non valid color')
		}
		else if (!(isValidPos(x) && isValidPos(y))) {
			throw_message('given position of point i\'snt valid')
		}
		else {
			let color = colors[color_idx].css_format();
			// check if board is ready
			if (this.is_ready) {
				this._setAt(x, y, color)
			}
			// if not push to pixelQueue
			else {
				this.pixelQueue.push({
					x: x,
					y: y,
					color: color
				}); // insert
			}
		}
	},
	/**
	 * loadPixelQueue empty the pixel queue
	 */
	loadPixelQueue() {
		while (this.pixelQueue.length != 0) {
			let top_pixel = this.pixelQueue.shift(); // remove
			this._setAt(top_pixel.x, top_pixel.y, top_pixel.color);
		}
		this.is_ready = true;
		// case of set during setting board is_ready, 
		// (tiny chance of colliding but its very little)
		if(this.pixelQueue.length != 0){
			let top_pixel = this.pixelQueue.shift(); // remove
			this._setAt(top_pixel.x, top_pixel.y, top_pixel.color);
		}
		// then draw board
		this.drawBoard();
	},
	/**
	 * fix center position by mapFrags
	 */
	centerPos(cx, cy) {
		// center axis - (window_axis_size / 2 / mapFrags.scale)
		let divisor = 2 * mapFrags.scale
		this.x = Math.floor(cx - this.canvas[0].width / divisor)
		this.y = Math.floor(cy - this.canvas[0].height / divisor)
		// update offset of pen
		pen.updateOffset()
		board.drawBoard();
	},
	/**
	 * sets the canavs zoom level
	 * @see {@link https://www.html5rocks.com/en/tutorials/canvas/hidpi/}
	 */
	updateCanvasZoom() {
		// set size of board
		let ratio = devicePixelRatio
		let width = innerWidth * ratio;
		let height = innerHeight * ratio;
		this.canvas[0].width = width;
		this.canvas[0].height = height;
		// scale canvas for devicePixelRatio for better scaling
		this.getCanvasContext().scale(ratio, ratio)
		this.centerPos(mapFrags.cx, mapFrags.cy);
		this.drawBoard()
	},
	/**
	 * update zoom level
	 */
	updateZoom() {
		this.updateCanvasZoom();
		pen.updateOffset();
		// refresh zoom style
		mapFrags.refreshZoomStyle();
	},
	/**
	 * update Coordination displayed
	 */
	updateCoords() {
		// not (A or B) == (not A) and (not B)
		if ($('#coordinates').is(':hover')) {
			$('#coordinate-slicer').text('copy')
			$('#coordinateX').text('');
			$('#coordinateY').text('');
		}
		else if (!pen.isDragged()) {
			$('#coordinate-slicer').text(pen.isAtBoard ? ',' : 'None');
			$('#coordinateX').text(pen.isAtBoard ? pen.x : '');
			$('#coordinateY').text(pen.isAtBoard ? pen.y : '');
		}
	},
	/**
	 * draw the board
	 * first the function checks if the board already called this method
	 * before the last animation loop or isnt ready, if so doesnt need to be redrawn
	 * then calls for the requestAnimationFrame
	 */
	drawBoard() {
		// if board isn't ready or don't need to draw
		if (board.needs_draw || !board.is_ready) {
			return;
		}
		this.needs_draw = true;
		requestAnimationFrame(
			() => { // 1-5 millisecond call, for all animation
				// it seems the average time of 5 operations is 0.23404487173814767 milliseconds
				//t = performance.now();
				// needs_draw = false
				this.needs_draw = false;
                // draw background
                let canvas_context = this.getCanvasContext();
				canvas_context.fillStyle = BACKGROUND_COLOR
				canvas_context.fillRect(0, 0, innerWidth, innerHeight);
				// save current state, to zoom for board
				canvas_context.save()
				// set imageSmoothingEnabled, good for pixel art
				/** @see {@link https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/imageSmoothingEnabled} */
				canvas_context.imageSmoothingEnabled = false;
				// zoom in the amout of scale
				canvas_context.scale(mapFrags.scale, mapFrags.scale)
				// scroll the board negativly the position we are relative to created
				// illusion of we are looking at him in that position
				// (left to me is right to him)
				canvas_context.translate(-this.x, -this.y);
				// draws the image on canvas
				canvas_context.drawImage(this.img_canvas, 0, 0);
				//  draws pen
				if (pen.canDrawPen()) {
					canvas_context.fillStyle = colors[pen.color].css_format(0.6);
					canvas_context.fillRect(pen.x, pen.y, 1, 1);
				}
				canvas_context.restore(); // return to default position
			});
	},
};

/**
 * @namespace
 * @desc object used to represent the lock state of the board
 */
const lockedState = {
	/** 
     * @type {boolean}
     * @desc if board is locked
     */
	_locked: false,
	/**
	 * @returns {boolean} _locked vaule
	 * returns if the board is locked, simple get function
	 */
	get locked() {
		return this._locked;
	},
	/**
	 * 
	 * @param {boolean} alert if to show the alert
	 * locks the board 
	 */
	lock(alert=false) {
		this._locked = true;
		$('#lock-colors').attr('lock', 1);
		if(alert){
			Swal.fire({
				icon:'info',
				title:'Board is locked'
			})
		}
	},
	/**
	 * @param {boolean} alert if to show alert
	 * handles the execution
	 */
	unlock(alert) {
		this._locked = false;
		$('#lock-colors').attr('lock', 0);
		if(alert){
			Swal.fire({
				icon:'info',
				title:'Board is unlocked'
			})
		}
	},
}

/**
 * @param {KeyPressEvent} key_event 
 * key press event handling for document
 * @see {@link https://stackoverflow.com/a/9310900} 
 */
function DocumentKeyPress(key_event){
	switch (key_event.code) {
		// toggle toolbox up
		case 'KeyX': {
			$('#toggle-toolbox-button').click();
			break;
		}
		// select color to the right
		case 'KeyC': {
			let button = $(".colorButton[picked='1']").first();
			// if any of the is undefiend - reset
			if (_.isUndefined(button[0]) || _.isUndefined(button.next()[0])) {
				button = $(".colorButton").first()
			}
			pen.setColorButton(button.next())
			break;
		}
		// select color to the left
		case 'KeyZ': {
			let button = $(".colorButton[picked='1']");
			if (_.isUndefined(button) || _.isUndefined(button.prev()[0])) {
				button = $('.colorButton').last()
			}
			pen.setColorButton(button.prev())
			break;
		}
		// go to keyboard mode or draw pixel in keyboard mode
		case 'KeyP': {
			// force keyboard if not in keyboard mode, else color a pixel
			if (pen.is_in_center_mode && isSwalClose()) {
				pen.setPixel();
			}
			else if (!pen.is_in_center_mode) {
				pen.setCenterPos()
			}
			break;
		}
		// toggle zoom states
		case 'KeyT': {
			// press the zoom button
			nonSweetClick('#zoom-button')
			break;
		}
		// toggle between full screen
		case 'KeyF': {
			// press the F button
			nonSweetClick('#screen-button')
			break;
		}
		default: {
			// do nothing
			break;
		}
	}
	// zoom bigger or smaller
	if (key_event.originalEvent.shiftKey) {
		if (key_event.originalEvent.key == '+') // key for plus
		{
			// option 0.5
			mapFrags.setScale(mapFrags.scale >= 1 ? mapFrags.scale + 1 : 1);
		}
		else if (key_event.originalEvent.key == '_') { // key for minus
			// option 0.5
			mapFrags.setScale(mapFrags.scale > 1 ? mapFrags.scale - 1 : MIN_SCALE);
		}
	}
}

/**
 * recursive function to get the board
 */
function fetchBoard() {
	sock.emit('get-start', (data) => {
		if(!(_.isUndefined(data) || _.isNull(data) || _.isNull(data.locked) || _.isNull(data.board))){
			progress.setTime(data.time)
			board.buildBoard(new Uint8Array(data.board));
			if (data.locked) {
				lockedState.lock();
			}
		} else {
			Swal.fire({
				icon:'warning',
				title:'Fail',
				text:'Fail to collect data from the server',
				allowOutsideClick: false
			}).then(() =>{
				// retry
				_.delay(
					() => {
						// clear pixel queue to prevent long time pushing
						board.pixelQueue = [];
						fetchBoard();
					}, FETCH_BOARD_INTERVAL
					// wait 5 seconds before retry
				);
			});
			// also clear board.queue
		}
	});
}


$(document).ready(function() {
	// init all buildBoard releated objects
	mapFrags.preRun();
	progress.preRun();
	board.preRun();
	pen.preRun();
	sock.on('connect', function() {
		// loop until get board
		fetchBoard();
	})
    // connect socket
    sock.connect()
    // fix location of mapFrags, also to remove html argument
    mapFrags.fixLocation();
    // when board is set
	sock.on('set-board', (x, y, color_idx) => board.setAt(x, y, color_idx));
	// when lock state changed
	sock.on('change-lock-state', (new_state) => {
		// if new state is active that means true
		if (new_state) {
			// unlock board
			lockedState.unlock();
		} else {
			// lock board
			lockedState.lock();
		}
	});
	// reconnection message
	sock.on('reconnect', () => {
		Swal.fire({
			icon: 'success',
			title: 'Reconnected to the server',
			text: 'Server Connection returned',
		})
	});
	// shows fail connection message
	sock.on('reconnect_error', () => {
		board.resetBoardBuild();
		//staff
		Swal.fire({
			icon: 'error',
			title: 'Connection Lost',
			text: 'Lost Connection with the server',
		})
	})
	// update coordinates when hover on them or leaves them, to copy them
	$('#coordinates').hover(function() {
		board.updateCoords();
	}, function() {
		board.updateCoords();
	});
	// set color
	board.canvas.mousemove((mouse_move_event) => {
		pen.setPenPos(mouse_move_event);
		// change scale by mouse wheel
	}).mouseleave(() => pen.clearPos()).bind('mousewheel', (wheel_event) => {
		// mousewheel event for moving
		wheel_event.preventDefault();
		mapFrags.setScale(
			clamp(
				mapFrags.scale + Math.sign(wheel_event.originalEvent.wheelDelta) * 1,
				MAX_SCALE,
				MIN_SCALE
			)
		);
	// draw pixel by double click
	})[0].addEventListener('dblclick', (double_click_event) => {
		// @see {@link https://github.com/Leaflet/Leaflet/issues/4127}
		// @see {@link https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/}
		pen.setPenPos(double_click_event)
		cursor.setPen();
		pen.setPixel();
	});
	// mouse down, start drag
	board.canvas.mousedown(function(mouse_down_event) {
		pen.drag_data = new DragData(mapFrags.cx, mapFrags.cy, mouse_down_event.pageX, mouse_down_event.pageY)
	// set pen when locking at board
	}).mouseenter(function() {
		cursor.setPen();
	})
	// move dragger
	$(document).mousemove(function(mouse_event) {
		if (pen.isDragged()) {
			mapFrags.centerOn(pen.drag_data.getDraggedPos(
				[mouse_event.pageX, mouse_event.pageY],
				mapFrags.scale
			));
			// Change to grab cursors
			cursor.grab();
		}
		// stop draw board
	}).mouseup(() => {
		// clear drag data
		pen.stopDrag();
		cursor.setPen();
	})
	$(document)
	/** @see DocumentKeyPress */
	.keypress(DocumentKeyPress)
	// keydown
	.keydown((key_down_event) => {
		// stack overflow
		let key_name = key_down_event.key;
		if(_.has(DirectionMap, key_name)){
			let movement_direction = DirectionMap[key_name];
			if ((movement_direction instanceof KeyDirection) && movement_direction.setIfCleared()) {
				board.addMovement(movement_direction.direction);
			}
		}
	}).keyup((key_up_event) => {
		let key_name = key_up_event.key;
		// find form direction map
		if(_.has(DirectionMap, key_name)){
			let movement_direction = DirectionMap[key_name];
			if ((movement_direction instanceof KeyDirection) && movement_direction.clearIfSet()) {
				board.subMovement(movement_direction.direction);
			} else {
				return;
			}
		}
		// go home page
		else if (key_name == 'Home') {
			nonSweetClick('#home-button');
		}
		// ESC => exit
		else if (key_name == 'Escape') { // Escape Option
			// prevent event collision with swal ESCAPE
			nonSweetClick('#logout-button');
		}
	});
	// toggle toolbox
	$('#toggle-toolbox-button').click(function(e) {
		e.preventDefault();
		let toolbox = $('#toolbox')[0];
		// fade icons and move the toolbox down by setting its hide attribute to 1
		if (toolbox.getAttribute('hide') == '0') {
			$('.icon-button').fadeOut(500);
			toolbox.setAttribute('hide', '1')
		}
		else {
			// reveal icons
			$('.icon-button').fadeIn(500)
			toolbox.setAttribute('hide', '0')
		}
	});
	// hash change
	// if isnt refreshed change otherwise 
	window.addEventListener('hashchange', function(e) {
		if(mapFrags.refreshFragments()){
			board.drawBoard();
			mapFrags.fixHash()
		} else if(!mapFrags.doesHashMatch()) {
			mapFrags.fixHash()
		}
		e.preventDefault()
	}, false);
	// copy coords - https://stackoverflow.com/a/37449115
	let clipboard = new ClipboardJS('#coordinates', {
		text: function() { return window.location.origin + window.location.pathname + mapFrags.asArgument()(); }
	});
	// clipboard to copy board
	clipboard.on('success', function() {
		throw_message('Copy Success');
	})
	clipboard.on('error', function() {
		throw_message('Copy Error');
	})
	// change zoom level
	$('#zoom-button').click(function() {
		mapFrags.setScale($(this).children().hasClass('fa-search-minus') ? ZOOMED_OUT_DEFAULT_LEVEL : ZOOMED_IN_DEFAULT_LEVEL)
	});
	//logout
	$('#logout-button').click((e) => {
		// if there is any keypressed
		if (e) {
			e.preventDefault();
		}
		// swal leave event
		Swal.fire({
			title: 'Are you sure?',
			text: "Are you sure you want to leave now",
			icon: 'question',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: 'red',
			confirmButtonText: 'Yes',
			cancelButtonText: 'No'
		}).then((result) => {
			if (result.value) {
				window.location.href = '/logout';
			}
		});
	});
	// click on home button
	$('#home-button').click(function() {
		Swal.fire({
			title: 'return Home?',
			text: "Are you sure you want to leave to the home page",
			icon: 'question',
			showCancelButton: true,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: 'red',
			confirmButtonText: 'Yes',
			cancelButtonText: 'No'
		}).then((result) => {
			if (result.value) {
				window.location.href = '/';
			}
		});
	});
	// color color buttons
	$('.colorButton').each(function() {
		$(this).css('background-color', colors[parseInt($(this).attr('value'))].css_format()); // set colors
	}).click(function(event) {
		event.preventDefault(); // prevent default clicking
		pen.setColorButton($(this))
	});
	// go to new window
	//https://stackoverflow.com/a/11384018
	$('#chat-button').click((function() {
		// gets the refernese
		window.open(this.getAttribute('href'), '_black')
	}));
	// screen button -> fullscreen exit or enter
	$('#screen-button').click(function() {
		if (this.getAttribute('state') == '0') {
			openFullscreen();
		}
		else {
			CloseFullscreen();
		}
	})
	// on fullscreen state changed
	document.onfullscreenchange = function() {
		let not_state = $('#screen-button').attr('state') == '1' ? '0' : '1'
		$('#screen-button').attr('state', not_state);
	}
	// on resize
	$(window).resize(() => {
		// update canvas zoom
		board.updateCanvasZoom();
	})
});