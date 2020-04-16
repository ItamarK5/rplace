
/** @const BACKGROUND_COLOR */
const BACKGROUND_COLOR = '#777777'

/**  @const CANVAS_SIZE size of the canvas */
const CANVAS_SIZE = 1000;

/** @const MIN_SCALE minimum scale power limit */
const MIN_SCALE = 0.5;

/** @const MAX_SCALE minimum scale power limit */
const MAX_SCALE = 50;

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

/** @namespace modules
 *  modules used in app
 *  @param {SocketIO} io io module, for talking with server
 *  @param {SweetAlert} Swal alert 
 *  @param {Underscore} _ module contains utilities functions
 *  @param {ClipboardJS} ClipboardJS module to work clipboard, copying and pasting data (url)
 * 
 */
const io = window.io;
const Swal = window.Swal;
const _ = window._;
const ClipboardJS = window.ClipboardJS;



/** @const {number} SIMPLE_ZOOM_LEVEL the default big zoom level */
const SIMPLE_ZOOM_LEVEL = 40;

/** @const {number} SIMPLE_UNZOOM_LEVEL the default small zoom level */
const SIMPLE_UNZOOM_LEVEL = 4;

/** @const {number} DEFAULT_START_AXIS the center of the board 500, where starting if no other arguments are found {@link mapFrags} */
const DEFAULT_START_AXIS = 500;

/** @const {io.SocketIO} the scoketio object to talk with the server */
const sock = io('/paint', {
    autoConnect: false,
    transports: ['websocket'] // or [ 'websocket', 'polling' ], which is the same thing
});

/**@function
 * @summary wrapper function to recconect using io, to only run it 5 seconds after sock.io run it
 */
const try_reconnect = _.throttle(() => sock.try_reconnect(), 5000, {leading: false, trailing:false})

/**
 * @function
 * @template T
 * @param {T[]} group group of objects
 * @returns {?T} first item or null
 * returns returns first item in group, if cant returns null
 */
const getFirstIfAny = (group) => !group ? null : group[0]

/**
 * @function
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
 * @summary max CANVAS_SIZE, min limit 0
 */
const isValidPos = v => 0 <= v && v < CANVAS_SIZE;

/**
 * 
 * @param {*} num value suppose to be index of a Palette color (look down)
 * @returns {boolean} if its a valid color index
 * @summary between(0, 16) include and in number
 */
const isValidColor = num => typeof num == 'number' && num >= 0 && num < 16
/**
 * @returns {boolean} if there any sweet alerts messages open
 */
const isSwalClose = () => _.isUndefined($('.swal2-container')[0])

/**
 * @returns {number} time in UTC
 * @summary get current UTC time
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
 * @function
 * @returns {?number} map frag val or null
 * @summary get a map pos value from regex check
 */
const getMapPos = _.compose(
    parseInt, 
    getFirstIfAny
)

/**
 * @function
 * @returns {?number} map frag val or null
 * @summary get a map scale value from regex check
 */
const getMapScale = _.compose(
    parseFloat, getFirstIfAny
)


/* View in fullscreen */
/**
 * @summary open full screen
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
 * @summary close full screen (use also for non support)
 * https://www.w3schools.com/howto/howto_js_fullscreen.asp
 */
 function closeFullscreen() {
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
 * @summary if there are no alerts by the sweetalert extension open, the command executes clicking on a selector
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
 * @memberof Vector2D
 * @param {*} caller 
 * @param {function} call 
 * wraps a single parameter method of vector simple function of operation with scalars
 * for the use of the XY functions
 */


/**
 * @constructor
 * @classdesc class to use with direction map
 * @see {@link:DirectionMap}
 * @property {Vector2D} direction a vector represeting a direction to move
 * @property @private {boolean} if key is pressed
 */
function KeyDirection(direction) {
    this.direction = direction;
    this.__is_set = false;
    /**
     * clears the __is_set property, if the property was set
     * @returns {boolean} if this.__is_set value was true before the function
     */
    this.clearIfSet = function(){
        if(this.__is_set){
            this.__is_set = false;
            return true;
        }
        return false;
    }
    /**
     * sets the __is_set property, if the property was cleared
     * @returns {boolean} if this.__is_set value was false before the function
     */
    this.setIfCleared = function(){
        if(!this.__is_set){
            this.__is_set = true;
            return true;
        }
        return false;
    }
}


/**
 * @namespace DirectionMap
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
 * @class SimpleInterval
 * @classdesc SimpleInterval is a class that represent a "worker" which
 * executes a function each X time
 * the function uses the Interval API for works
 */
class SimpleInterval {
    /**
     * @param {function} work 
     * @param {number} time 
     */
    constructor(work, time) {
        /** @param {function} work */
        this.work = work;
        /** @param {function} time */
        this.__time = time;
        /** @param {function} __work_handler */
        this.__work_handler = null;
    }
    /**
     * @summary start the worker
     * @returns nothing
     */
    start() {
        this.__work_handler = setInterval(this.work, this.__time);
    }
    /**
     * @summary stops the worker
     */
    stop() {
        clearInterval(this.__work_handler)
        this.__work_handler = null
    }
    /**
     * @returns if the worker starts to work (and hasnt already worked)
     * safely starts the worker, only if the worker isn't already working
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
     * @summary checks if the worker is working at all using the handler
     */
    get isWorking() {
        return !_.isNull(this.__work_handler);
    }
}

/**
 * @class CursorState
 * @classdesc represents state of cursor, if to show the colored pixel that is how the pen is made or not 
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
     * checks if the curser equals to the other object
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
 * @summary contains the possible cursors uses the CursorState
 * @enum {CursorState}
 */
const Cursors = {
    pen: new CursorState('crosshair', false),
    wait: new CursorState('not-allowed', false),
    grabbing: new CursorState('grabbing', true),
    find_mouse: new CursorState('wait', true)
}

/**
 * @class Color
 * @property {number} red red value of the color in rgb
 * @property {number} green green value of the color in rgb
 * @property {number} blue blue value of the color in rgb
 * @property {name} name of the color
 * simple class to represent colors the can be placed on the board, the colors are saved as in RGB format
 */
class Color {
    /**
     * @param {number} r the r value
     * @param {number} g the green value
     * @param {number} b blue value of the color in rgb
     * @param {string} name name of the color
     * @returns new Color object
     * @summary basic paramter-value constructor
     */
    constructor(red, green, blue, name) {
        this.red = red;
        this.green = green;
        this.blue = blue;
        this.name = name;
    }
    /**
     * @returns {number} abgr values
     * @summary calculates abgr value
     * caluclates abgr value of color, opposite order to rgba because bit position
     */
    get abgr() {
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
 * @name colors an object holding the colors and handling interactions with them
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
 * @namespace progress
 * @description progress object handles all related staff to the progress bar on the screen
 * @property {number} time time of the progress
 * @property {number} state the state of the progress
 * @property {SimpleInterval} __work SimpleInterval for updating auto update the progress bar.  handler of progress update interval
 * @property {string} name SimpleInterval for updating auto update the progress bar
 * @property {boolean} isWaiting if waits for progress bar to end
 */
const progress = {
    time: 0, // time when cooldown ends
    state: 0, // state of progress bar
    __work: null, // handler of progress update interval
    __current_min_time: null,
    /**
     * constructor, the object initialization
     * sets his work
     */
    preRun() {
        let self = this;
        this.__work = new SimpleInterval(function() {
            self.updateTimer()
        }, PROGRESS_COOLDOWN)
    },
    /** @returns {boolean} if progress still works*/
    get isWaiting(){
        return this.__work.isWorking
    },
    /**
     * @param {number} seconds_left number of seconds before the progress bar ends
     * @summary update the progress bar text and state
     */
    adjustProgress(seconds_left) {
        // adjust the progress bar and time display by the number of seconds left
        $('#prog-text').text([
            (Math.floor(seconds_left / 60)).toString(),
            (seconds_left % 60).toString().padStart(2, '0')
        ].join(':'))
        // update progress fill
        // update area colored
        $('#prog-fill').css('width', (100 - (seconds_left / DRAW_COOLDOWN) *
            100) + "%");
        // 1 if time less then halve the number of seconds 
        this.state = Math.ceil(seconds_left * 2 / DRAW_COOLDOWN);
        $('#time-prog').attr('state', this.state);
    },
    /**
     * @param {string} time when the date finishes 
     * @summary set the time for the progress and start working
     */
    setTime(time) {
        // handles starting the timer waiting
        this.time = Date.parse(time + ' UTC');
        // if current time is after end of cooldown
        if (this.time < getUTCTimestamp()) {
            $('prog-text').text('0:00'); // set text 0
            $('#prog-fill').attr('state', 1); // prog-fill state is 9
            $('#time-prog').attr('state', 0); // time progress set to 1
            if (this.isWaiting) { // stop work in case
                this.__work.stop();
            }
        }
        // when stops working
        else if (!this.isWaiting) {
            this.__current_min_time = 300;
            this.__work.start()
            // set cursor to be pen
            cursor.setPen();
        }
    },
    /**
     *  @summary the function the worker runs, to update every x milliseconds the progress bar dom object
     *  @description
     *  Updates the progess bar and timer each interval
     *  Math.max the time until cooldown ends in ms, compare if positive (the time has not passed),
        ceil to round up, I want to prevent the progress showing time up to that
     */
    updateTimer() {
        let seconds_left = Math.ceil(Math.max(this.time - getUTCTimestamp(),
            0) / 1000);
        // adjust progress
        if (this.__current_min_time != seconds_left) {
            this.adjustProgress(seconds_left);
            // update current time
            this.__current_min_time = seconds_left;
        }
        // close for cooldown 0
        if (seconds_left <= 0) {
            // clear Interval
            this.stopProgress();
        }
    },
    /**
     * stops the progress bar
     */
    stopProgress() {
        this.__work.stop();
        cursor.setPen();
    }
}

/**
 * @namespace mapFrags
 * @property {?number} cx the x position of the pixel at the center of the screen 
 * @property {?number} cy the y position of the pixel at the center of the screen
 * @property {?number} scale the amount of zoom on the screen
 * @method fixHash sets the hash of the object
 * @description handles working with the url and movement of the board
 */
const mapFrags = {
    /**
     * @method
     * wraps __fixHash function with _.throttle function
     * throttle executes the function once every x time, and if the function was called during the waited time,
     * it executes it when the time ends.
     * @see {@link https://underscorejs.org/#throttle}
     */
    fixHash: null,
    /**
     * initialize the object, all related document function, runs when document is ready
     */
    preRun() {
        // set window hash to be valid
        this.fixHash = _.throttle(this.__fixHash, 1000);
        let fragments = this.__determineFragments();
        this.cx = fragments.x;
        this.cy = fragments.y;
        this.scale = fragments.scale;
    },

    doesHashMatch(){
        return mapFrags.hash() != window.location.hash;
    },
    /**
     * @returns calculates size of step (amount of window pixels that fit 1 board pixel) in pixels
     * calculates size of step, used for other functions
     */
    get step() {
        return MAX_SCALE / mapFrags.scale;
    },

    /**
     * @private
     * @returns {string} the raw path for the map
     */
    get __path() {
        return `x=${this.cx}&y=${this.cy}&scale=${this.scale}`
    },
    /**
     * @returns {string} hash params of the url with the same map position
     */    hash() {
        return `#${this.__path}`
    },
    /**
     * @returns {string} arguments param of the url with the same map position
     * the value for location's hash field to set mapFrags as current
     */
    arguments() {
        return `?${this.__path}`
    },
    /**
     * @param {Vector2D} vector represent the new center
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
    __isValidNewX(new_x) {
        return (!isNaN(new_x)) && isValidPos(new_x) && new_x != this.cx
    },
    /**
     * 
     * @param {number} new_y 
     * @returns {boolean} if the param can be the next cy value (next value means its different from current)
     * if value is valid 'new' center y
     */
    __isValidNewY(new_y) {
        return (!isNaN(new_y)) && isValidPos(new_y) && new_y != this.cy
    },
    /**
     * @param {number} new_scale 
     * @returns {boolean} if the param can be the next cy value (next value means its different from current)
     * if value is valid 'new' scale
     */
    __isValidNewScale(new_scale) {
        return (!isNaN(new_scale)) && isValidScale(new_scale) && new_scale != this.scale
    },
    /**
     * @returns the x position the board suppose to be on the screen.
     * @summary the function first check by the arguments, then by the hash and finally by the favorable position
     * determine x locaiton by checking fields
     * first check the arguments
     * then checks the hash
     * after the current center x
     * then checks for default
     * and in the end, returnd default DEFAULT_CENTER_AXIS (500)
     */
    __determineX() {
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
        if(_.isNumber(this.cx)){
            return this.cx;
        }
        // else search for value in body
        x = parseInt($('body').attr('x'))
        if ((!isNaN(x)) && isValidPos(x)) {
            return x;
        }
        return DEFAULT_START_AXIS;
    },
    /**
     * @returns the y position the board suppose to be on the screen.
     * @summary the function first check by the arguments, then by the hash and finally by the favorable position
     * determine scale value by checking fields
     * first the arguments
     * then checks the hash
     * after the current scale (this.scale)
     * then checks for default
     * and in the end, returnd default zoom level (4)     */
    __determineY() {
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
        if(_.isNumber(this.cy)){
            return this.cy;
        }
        y = parseInt($('body').attr('y'))
        if ((!isNaN(y)) && isValidPos(y)) {
            return y;
        }
        return SIMPLE_UNZOOM_LEVEL;
    },
    /**
     * @returns the y position the board suppose to be on the screen.
     * @summary the function first check by the arguments, then by the hash and finally by the favorable position
     */
    __determineScale() {
        let scale = getMapScale(window.location.search.match(reArgScale));
        if ((!isNaN(scale)) && isValidScale(scale)) {
            return scale;
        }
        // second get from hash
        scale = getMapScale(window.location.hash.match(reHashScale))
        if ((!isNaN(scale)) && isValidScale(scale)) {
            return scale;
        }
        if(_.isNumber(this.scale)){
            return this.scale;
        }
        // else search for value in body
        scale = parseFloat($('body').attr('scale'))
        if ((!isNaN(scale)) && isValidScale(scale)) {
            return scale;
        }
        return SIMPLE_UNZOOM_LEVEL;
    },
    moveBoard(dx, dy) {
        mapFrags.setCenter(
            clamp(mapFrags.cx + dx * this.step, CANVAS_SIZE, 0),
            clamp(mapFrags.cy + dy * this.step, CANVAS_SIZE, 0)
        );
    },
    /**
     * @returns the fields of the object
     * determine the current fragments and update board
     */
    __determineFragments() {
        return {
            x: this.__determineX(),
            y: this.__determineY(),
            scale: this.__determineScale()
        };
    },
    /**
     * @param {number} x new x positon of the center of the viewport
     * @param {number} y new y positon of the center of the viewport
     * @param {boolean} to_update if to update the position, used when using the function with the setScale method
     * @returns {boolean} if the cx or cy fragments have been changed
     * @summary handles setting the new center, also prevent any changes if the scale level is less then 1 (0.5)
     */
    setCenter(x = undefined, y = undefined, to_update = true) {
        let flag = false;
        // if any undefined it returns NaN
        x = this.scale >= 1 ? Math.round(x) : CANVAS_SIZE / 2;
        y = this.scale >= 1 ? Math.round(y) : CANVAS_SIZE / 2;
        if (this.__isValidNewX(x)) {
            flag = true;
            this.cx = x;
        }
        if (this.__isValidNewY(y)) {
            flag = true;
            this.cy = y;
        }
        if (to_update && flag) {
            board.centerPos();
            this.fixHash();
        }
        return flag;
    },
    /**
     * @param {number} scale 
     * @param {boolean} to_update if to update the 
     * if the scale level is less then 0.5
     */
    setScale(scale, to_update = true) {
        if (this.__isValidNewScale(scale)) {
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
     * @summary handling changes to the fragments 
     */
    refreshFragments() {
        /*  refreshFragments(bool) -> void
         *  refresh the mapFrags object by the current hash values if they are valid
         */
        let frags = this.__determineFragments();
        let any_changes = frags.x != this.cx || frags.y != this.cy || frags.scale != this.scale;
        if(any_changes){
            this.setCenter(frags.x, frags.y, this.__isValidNewScale(frags.scale));
            if (this.__isValidNewScale(frags.scale)) {
                this.scale = frags.scale;
                board.updateZoom();
            }
        }
        return any_changes;
        
    },
    /**
     * @summary private function handling fixing the hash displayed
     * another function wraps it to make it only be only x time after the last the function was called
     */
    __fixHash() {
        //  update location
        // first tried to update event set
        // now lets try using setTimeout
        if (this.doesHashMatch()) {
            // change hash without triggering events
            // https://stackoverflow.com/a/5414951
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
    }
}

/** @namespace cursor  
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
     * @summary sets the new cursor
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
     * @summary updates the cursor state
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
        this.updateCursor(progress.isWorking || lockedStates.locked ? Cursors.wait : Cursors.pen)
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

/**@namespace pen 
 * @property {number} x the x position the mouse points to (on the board else null)
 * @property {number} y the y position the mouse points to (on the board else null)
 * @property {?number} __color the color of the pen
 * @property {number[]} last_mouse_pos the (x,y) position the mouse moved to (if its on the board)
 * @property {boolean} is_in_center_mode if the pen is in center mode == key movement mode
 * @property {boolean} __disable if the pen is in disabled mode, invincible
 * @property {string} cursor_style  the cursor style to put the mouse on
*/
const pen = {
    x: -1,
    y: -1,
    __color: null,
    last_mouse_pos: null,
    is_in_center_mode: true,
    __disable: false,
    cursor_style: 'default',
    /**
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
     * clears the canvas pen and updates the board
     */
    disable() {
        // if not disabled don't do anything
        if (!this.__disable) {
            this.__disable = true;
            board.drawBoard();
        }
    },
    /**
     * resets the canvas pen and updates the board
     */
    enable() {
        if (this.__disable) {
            this.__disable = false;
            board.drawBoard();
        }
    },
    /**
     * 
     * @param {?jQuert.Event} e $ event that wraps a mouse event, if not restores from last one used
     * @summary the mouse position (if there is not event,resets then to last)
     */
    getMouseOffset(e) {
        if (e) {
            // set last_mouse_pos
            this.last_mouse_pos = [e.pageX, e.pageY]
        }
        return this.last_mouse_pos;
    },
    /**
     * 
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
     * 
     * @param {jQuery.Event} e mouse event
     * updates the offset and stop the keyboard mode 
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
     * 
     * @param {jQuery} button 
     * sets the color of the button as the pens color also set the button to focused (means thats the color of the pen)
     */
    setColorButton(button) {
		this.color = parseInt(button.attr('value'));
        $('.colorButton[picked="1"]').attr('picked', '0');
        button.attr('picked', '1');
    },
    /**@returns {boolean} if has color */
    get hasColor() {
        return isValidColor(this.__color);
    },
    /**@returns {number} index of pen color */
    get color() {
        return this.__color;
    },
    /**
     * @param {number} value
     */
    set color(value) {
        if (value >= 0 && value < 16 && this.__color != value) {
            this.__color = value;
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
     * can se pixel if pen isnt disabled, has color and is at board
     */
    canDrawPen() {
        return (!this.__disable) && this.hasColor && this.isAtBoard
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
                confirmButtonText: 'To Waiting'
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
        else if (progress.isWaiting) {
            Swal.fire({
                title: 'You have 2 wait',
                imageUrl: 'https://aadityapurani.files.wordpress.com/2016/07/2.png',
                imageHeight: 300,
                imageAlt: 'wow that was rude',
                text: 'Wait for your cooldown to end'
            });
        }
        // if locked
        else if (lockedStates.locked) {
            Swal.fire({
                title: 'Canvas is closed',
                imageUrl: 'https://img.memecdn.com/door-lock_o_2688511.jpg',
                imageHeight: 250,
                imageAlt: 'Social Painter Dash canvas is currently locked',
                text: 'Wait an admin will open it up',
                confirmButtonText: 'To Waiting'
            });
        }
        else if (!this.hasColor) {
            Swal.fire({
                icon: 'warning',
                title: 'Select Color',
                text: 'pless select color from the table',
            });
        }
        else {
            sock.emit('set-board', {
                'color': this.__color,
                'x': this.x,
                'y': this.y,
            }, (value) => {
                if (_.isUndefined(value) || value == 'undefined') {
                    return;
                }
                // else it must be json
                let data = JSON.parse(value);
                if (data.code == 'lock' && data.status == 'true') {
                    lockedStates.lock()
                } else if (data.code == 'time') {
                    progress.setTime(data.status)
                }
            });
        }
    }
}


/** @constructor
 * 
 * @param {number} start_x where started to drag (in x axis, measure by board pixels)
 * @param {number} start_y where started to drag (in y axis, measure by board pixels)
 * @param {number} drag_x  where the mouse press (in x axis, measure by screen pixels)
 * @param {number} drag_Y  where the mouse press (in y axis, measure by screen pixels)
 * DragData constructor, object representing the information the board being dragged
 */
function DragData(start_x, start_y, drag_x, drag_y) {
    this.start_vector = new Vector2D(start_x, start_y);
    this.drag_vector = new Vector2D(drag_x, drag_y)
    /**
     * @method
     * @param {Vector2D} new_pos mouse event to check the new position of the mouse
     * @param {number} scale scale multiplayer
     * @returns {Vector2D} vector2d represent the position an object is dragged to
     */
    this.getDraggedPos = function(new_pos, scale){
        let dragged_position = this.drag_vector.clone().subVector(new_pos).divXY(scale);
        let v=new Vector2D(
            Math.floor(dragged_position.x) + this.start_vector.x,
            Math.floor(dragged_position.y) + this.start_vector.y
        )     
        return v;

    }
}


/** 
 * @namespace board 
 * @property $} img_canvas canvas to save the image of the board
 * @property {Uint8Array} buffer
 * @property {number} x space between head of the board to the x start of the page
 * @property {number} y space between head of the board to the x start of the page
 * @property {?DragData} drag drag information when dragging the board
 * @property {}
 * */
const board = {
    img_canvas: null,
    ctx_image: null,
    buffer: null,
    x: 0,
    y: 0,
    drag_data: null,
    canvas: null,
    needs_draw: false,
    move_vector: Vector2D.zero(),
    key_move_work: null,
    ctx: null,
    pixelQueue: [],
    buildBoard: null,
    is_ready:false,
    preRun() {
        this.buildBoard = _.once(this.__buildBoard);
        this.canvas = $('#board');
        this.img_canvas = document.createElement('canvas');
        this.img_canvas.width = CANVAS_SIZE;
        this.img_canvas.height = CANVAS_SIZE;
        this.ctx_image = this.img_canvas.getContext('2d');
        this.ctx = this.canvas[0].getContext('2d');
        let bind_move_board = _.bind(
             () => mapFrags.moveBoard(
                 this.move_vector.x,
                 this.move_vector.y
                ),
             this
        )
        this.key_move_work = new SimpleInterval(
            bind_move_board, 100
        )
        this.updateZoom(); // also centers
    },
    isDragged(){
        return !_.isNull(this.drag_data)
    },
    resetBoardBuild() {
        /**
         * reset values for board build
         */
        this.buildBoard = _.once(this.__buildBoard);
        board.is_ready = false
    },

    addMovement(dir) {
        this.move_vector.addVector(dir);
        mapFrags.moveBoard(dir.x, dir.y)
        this.key_move_work.safeStart();
    },
    subMovement(dir) {
        this.move_vector.subVector(dir);
        if (this.move_vector.isZero()) {
            this.key_move_work.safeStop();
        }
    },
    //buffer on chrome takes ~1552 ms -- even less
    __buildBoard(buffer) {
        let image_data = new ImageData(CANVAS_SIZE, CANVAS_SIZE);
        let image_buffer = new Uint32Array(image_data.data.buffer);
        buffer.forEach(function(val, index) {
            // first version of putting data, looping over the image buffer array and not of buffer of message
            //var bit = buffer[Math.floor(index/2)];
            //self.buffer[index] = reverseRGBA(COLORS[index % 2 == 0 ? bit % 16 : bit >> 4]);
            image_buffer[index * 2] = colors[val % 16].abgr; // small number
            image_buffer[index * 2 + 1] = colors[Math.floor(val / 16)].abgr; // big number
        });
        this.ctx_image.putImageData(image_data, 0, 0);
        this.beforeFirstDraw();
    },
    __setAt(x, y, color) {
        this.ctx_image.fillStyle = color;
        this.ctx_image.fillRect(x, y, 1, 1);
        this.drawBoard();
    },
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
            if (this.is_ready) {
                this.__setAt(x, y, color)
            }
            else {
                this.pixelQueue.push({
                    x: x,
                    y: y,
                    color: color
                }); // insert
            }
        }
    },
    // empty the pixel queen
    beforeFirstDraw() {
        while (this.pixelQueue.length != 0) {
            let top_pixel = this.pixelQueue.shift(); // remove
            this.__setAt(top_pixel.x, top_pixel.y, top_pixel.color);
        }
        this.is_ready = true;
        // case of set during setting board is_ready, (tiny chanse of colliding but its very little)
        if(this.pixelQueue.length != 0){
            let top_pixel = this.pixelQueue.shift(); // remove
            this.__setAt(top_pixel.x, top_pixel.y, top_pixel.color);
        }
        // draw board
        this.drawBoard();
    },
    centerPos() {
        // center axis - (window_axis_size / 2 / mapFrags.scale)
        let divisor = 2 * mapFrags.scale
        this.x = Math.floor(mapFrags.cx - this.canvas[0].width / divisor)
        this.y = Math.floor(mapFrags.cy - this.canvas[0].height / divisor)
        pen.updateOffset()
        board.drawBoard();
    },
    setCanvasZoom() {
        //https://www.html5rocks.com/en/tutorials/canvas/hidpi/
        let ratio = devicePixelRatio
        let width = innerWidth * ratio;
        let height = innerHeight * ratio;
        this.canvas[0].width = width;
        this.canvas[0].height = height;
        console.lo
        // scale canvas
        this.ctx.scale(devicePixelRatio, devicePixelRatio)
        this.centerPos();
        this.drawBoard()
    },
    updateZoom() {
        this.setCanvasZoom();
        pen.updateOffset();
        this.setZoomStyle();
    },
    setZoomStyle() {
        let zoom_button = $('#zoom-button')
        if (mapFrags.scale >= 25) {
            zoom_button.children('span').addClass('fa-search-minus').removeClass('fa-search-plus');
            zoom_button.css('cursor', 'zoom-out');
        }
        else {
            zoom_button.children('span').addClass('fa-search-plus').removeClass('fa-search-minus');
            zoom_button.css('cursor', 'zoom-in');
        }
    },

    updateCoords() {
        // not (A or B) == (not A) and (not B)
        if ($('#coordinates').is(':hover')) {
            $('#coordinate-slicer').text('copy')
            $('#coordinateX').text('');
            $('#coordinateY').text('');
        }
        else if (!board.isDragged()) {
            $('#coordinate-slicer').text(pen.isAtBoard ? ',' : 'None');
            $('#coordinateX').text(pen.isAtBoard ? pen.x : '');
            $('#coordinateY').text(pen.isAtBoard ? pen.y : '');
        }
    },
    drawBoard() {
        // if board isnt ready or dont need to draw
        if (board.needs_draw || !board.is_ready) {
            return;
        }
        this.needs_draw = true;
        requestAnimationFrame(
            () => { // 1-5 millisecond call, for all animation
                // it seems the average time of 5 operations is 0.23404487173814767 milliseconds
                //t = performance.now();
                console.log(this.x, this.y)
                this.needs_draw = false;
                this.ctx.fillStyle = BACKGROUND_COLOR
                this.ctx.fillRect(0, 0,innerWidth, innerHeight);
                this.ctx.save()
                this.ctx.imageSmoothingEnabled = false;
                this.ctx.scale(mapFrags.scale, mapFrags.scale)
                this.ctx.translate(-this.x, -this.y);
                this.ctx.drawImage(this.img_canvas, 0, 0);
                if (pen.canDrawPen()) {
                    this.ctx.fillStyle = colors[pen.color].css_format(0.6);
                    this.ctx.fillRect(pen.x, pen.y, 1, 1);
                }
                this.ctx.restore(); // return to default position
                //performance_arr.push(performance.now()-t)
            });
    },
};


const lockedStates = {
    __locked: false,
    get locked() {
        return this.__locked;
    },
    lock(alert=false) {
        this.__locked = true;
        $('#lock-colors').attr('lock', 1);
        if(alert){
            Swal.fire({
                icon:'info',
                title:'Board is locked'
            })
        }
    },
    unlock(alert) {
        this.__locked = false;
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
        case 'KeyX': {
            $('#toggle-toolbox-button').click();
            break;
        }
        case 'KeyC': {
            let button = $(".colorButton[picked='1']").first();
            // if any of the is undefiend - reset
            if (_.isUndefined(button[0]) || _.isUndefined(button.next()[0])) {
                button = $(".colorButton").first()
            }
            pen.setColorButton(button.next())
            break;
        }
        case 'KeyZ': {
            let button = $(".colorButton[picked='1']");
            if (_.isUndefined(button) || _.isUndefined(button.prev()[0])) {
                button = $('.colorButton').last()
            }
            pen.setColorButton(button.prev())
            break;
        }
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
        case 'KeyT': {
            nonSweetClick('#zoom-button')
        }
        case 'KeyG': {
            cursor.lockCursor(Cursors.find_mouse);
            break;
        }
        case 'KeyF': {
            nonSweetClick('#screen-button')
            break;
        }
        default: {
            break;
        }
    }
    if (key_event.originalEvent.shiftKey) {
        if (key_event.originalEvent.key == '+') // key for plus
        {
            // option 0.5
            console.log(mapFrags.scale >= 1, mapFrags.scale)
            mapFrags.setScale(mapFrags.scale >= 1 ? mapFrags.scale + 1 : 1);
        }
        else if (key_event.originalEvent.key == '_') { // key for minus
            // option 0.5
            mapFrags.setScale(mapFrags.scale > 1 ? mapFrags.scale - 1 : MIN_SCALE);
        }
    }
}

/**
 * Docuemnt event
 */
$(document).ready(function() {
    // init all buildBoard releated objects
    mapFrags.preRun();
    progress.preRun();
    board.preRun();
    pen.preRun();
    sock.on('connect', function() {
        sock.emit('get-starter', (data) => {
            progress.setTime(data.time)
            board.buildBoard(new Uint8Array(data.board));
            if (data.lock) {
                lockedStates.lock();
            }
        });
    })
    sock.connect()
    mapFrags.fixLocation();
    sock.on('set-board', (x, y, color_idx) => board.setAt(x, y, color_idx));
    // Lost connection
    // Connection on
    sock.on('change-lock-state', (new_state) => {
		// if new state is active that means true
        if (new_state) {
			// unlock board
			lockedStates.unlock();
        } else {
            // lock board
            lockedStates.lock();
        }
    });
    sock.on('reconnect', () => {
        Swal.fire({
            icon: 'success',
            title: 'Reconnected to the server',
            text: 'Server Connection returned',
        })
    });
    sock.on('reconnect_error', () => {
        board.resetBoardBuild();
        //staff
        Swal.fire({
            icon: 'error',
            title: 'Connection Lost',
            text: 'Lost Connection with the server',
        })
    })
    $('#coordinates').hover(function() {
        board.updateCoords();
    }, function() {
        board.updateCoords();
    });
    // set color
    board.canvas.mousemove((mouse_move_event) => {
        pen.setPenPos(mouse_move_event);
    }).mouseleave(() => pen.clearPos()).bind('mousewheel', (wheel_event) => {
        // mousewheel event for moving
        wheel_event.preventDefault();
        mapFrags.setScale(
            clamp(
                mapFrags.scale + Math.sign(e.originalEvent.wheelDelta) * 1,
                MAX_SCALE,
                MIN_SCALE
            )
        );
    })[0].addEventListener('dblclick', (dobule_click_event) => { // for not breaking the 
        // jmapFrags dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        pen.setPenPos(dobule_click_event);
        cursor.setPen();
        pen.setPixel();
    });
    board.canvas.mousedown(function(mouse_down_event) {
        board.drag_data = new DragData(mapFrags.cx, mapFrags.cy, mouse_down_event.pageX, mouse_down_event.pageY)
    }).mouseenter(function() {
        cursor.setPen();
    })
    $(document).mousemove(function(mouse_event) {
        if (board.isDragged()) {
            mapFrags.centerOn(board.drag_data.getDraggedPos(
                [mouse_event.pageX, mouse_event.pageY],
                mapFrags.scale
            ));
            // center board
            cursor.grab();
        }
    }).mouseup(() => {
        // clear drag data
        board.drag_data = null;
        cursor.setPen();
    })
    $(document)
    /** @see DocumentKeyPress */
    .keypress(DocumentKeyPress)
    .keydown((key_down_event) => {
        // stack overflow
        let key_name = (key_down_event || window.event).key;
        if(_.has(DirectionMap, key_name)){
            let movement_direction = DirectionMap[key_name];
            if ((movement_direction instanceof KeyDirection) && movement_direction.setIfCleared()) {
                board.addMovement(movement_direction.direction);
            }
        }
    }).keyup((key_up_event) => {
        let key_name = (key_up_event || window.event).key;
        if(_.has(DirectionMap, key_name)){
            let movement_direction = DirectionMap[key_name];
            if ((movement_direction instanceof KeyDirection) && movement_direction.clearIfSet()) {
                board.subMovement(movement_direction.direction);
            } else {
                return;
            }
        }
        // if home is unpressed, go home
        else if (key_name == 'Home') {
            nonSweetClick('#home-button');
        }
        else if (key_name == 'g') { // if g is pressed, release cursor state
            cursor.releaseCursor(Cursors.find_mouse)
        } else if (key_name == 'Escape') { // Escape Option
            // prevent event collision with swal ESCAPE
            nonSweetClick('#logout-button');
        }
    });
    // change toggle button
    $('#toggle-toolbox-button').click(function(e) {
        e.preventDefault();
        let toolbox = $('#toolbox')[0];
        // fade icons and move the toolbox down by setting its hide attribute to 1
        if (toolbox.getAttribute('hide') == '1') {
            $('.icon-button').fadeOut(500)
            toolbox.setAttribute('hide', '1')
        }
        else {
            // reveal icons
            $('.icon-button').fadeIn(500)
            toolbox.setAttribute('hide', '0')
        }
    });
    // hash change
    window.addEventListener('hashchange', function(e) {
        if(mapFrags.refreshFragments()){
            board.drawBoard();
            e.preventDefault()
        } else if(!mapFrags.doesHashMatch()) {
            mapFrags.fixHash()
        }
        e.preventDefault()
    }, false);
    // copy coords - https://stackoverflow.com/a/37449115
    let clipboard = new ClipboardJS('#coordinates', {
        text: function() { return window.location.origin + window.location.pathname + mapFrags.arguments(); }
    });
    clipboard.on('success', function() {
        throw_message('Copy Success');
    })
    clipboard.on('error', function() {
        throw_message('Copy Error');
    })
    // change zoom level
    $('#zoom-button').click(function() {
        mapFrags.setScale($(this).children().hasClass('fa-search-minus') ? SIMPLE_UNZOOM_LEVEL : SIMPLE_ZOOM_LEVEL)
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
    $('.colorButton').each(function() {
		$(this).css('background-color', colors[parseInt($(this).attr('value'))].css_format()); // set colors
    }).click(function(event) {
        event.preventDefault(); // prevent default clicking
        pen.setColorButton($(this))
    });
    //https://stackoverflow.com/a/11384018
    $('#chat-button').click((function(e) {
        window.open(this.getAttribute('href'), '_black')
    }));
    $('#screen-button').click(function() {
        if (this.getAttribute('state') == '0') {
            openFullscreen();
        }
        else {
            closeFullscreen();
        }
    })
    document.onfullscreenchange = function() {
        let not_state = $('#screen-button').attr('state') == '1' ? '0' : '1'
        $('#screen-button').attr('state', not_state);
    }
    let mqString = `(resolution: ${window.devicePixelRatio}dppx)`;

    const updatePixelRatio = () => {
        board.setCanvasZoom();
    }

    updatePixelRatio();
    // set color button
    $(window).resize((e) => {
        board.setCanvasZoom();
    })
});