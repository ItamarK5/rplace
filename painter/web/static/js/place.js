/* level of functions 1) the interaction 2) setting the query 3) a function that affect the board as result of change in query*/
const BACKGROUND_COLOR = '#777777'
const CANVAS_SIZE = 1000;
const MIN_STEP_SIZE = 1;
const MIN_SCALE = 0.5;
const MAX_SCALE = 50;
const DRAW_COOLDOWN = 60;
const PROGRESS_COOLDOWN = 50
const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;
const reHashScale = /(?<=(^#|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;
const reArgX = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;
const reArgY = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;
const reArgScale = /(?<=(^\?|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;
//const reHash = /(?<=(?:^#|.+&))([\w|\d]+)=([\w|\d]+)(?=&|$)/i
const DIRECTION_MAP = [
    {
        key: 'ArrowLeft',
        dir: [-1, 0],
        set: false
    }, // left
    {
        key: 'ArrowRight',
        dir: [1, 0],
        set: false
    }, // right
    {
        key: 'ArrowUp',
        dir: [0, -1],
        set: false
    }, // up
    {
        key: 'ArrowDown',
        dir: [0, 1],
        set: false
    } // down
];
const SIMPLE_ZOOM_LEVEL = 40;
const SIMPLE_UNZOOM_LEVEL = 4;
const DEFAULT_START_AXIS = 500;
const DEFAULT_SCALE_MULTIPLAYER = SIMPLE_ZOOM_LEVEL;
//const getOffset = (x, y) => (y * CANVAS_SIZE) + x;
const getFirstIfAny = (group) => _.isNull(group) ? null : group[0]
const clamp = (v, max, min) => Math.max(min, Math.min(v, max));
const is_valid_scale = scale => MIN_SCALE <= scale && scale <= MAX_SCALE;
const is_valid_pos = v => 0 <= v && v < CANVAS_SIZE;
const IsSwalClose = () => _.isUndefined($('.swal2-container')[0])
const getUTCTimestamp = () => {
    let tm = new Date();
    return Date.UTC(
        tm.getUTCFullYear(),
        tm.getUTCMonth(),
        tm.getUTCDate(),
        tm.getUTCHours(),
        tm.getUTCMinutes(),
        tm.getUTCSeconds(),
        tm.getUTCMilliseconds())
}
/**
 * 
 * @param {int} flag 
 */
const HashChangeFlag = {
    Needed: 'Needed',
    Disabled: 'Disabled',
    Enabled: 'Enabled'
}
const MaskHashChangeFlag = (flag) => flag == HashChangeFlag.Disabled ? HashChangeFlag.Needed : flag
/* View in fullscreen */
//https://www.w3schools.com/howto/howto_js_fullscreen.asp
function openFullscreen() {
    let elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    }
    else if (elem.mozRequestFullScreen) {
        /* Firefox */
        elem.mozRequestFullScreen();
    }
    else if (elem.webkitRequestFullscreen) {
        /* Chrome, Safari and Opera */
        elem.webkitRequestFullscreen();
    }
    else if (elem.msRequestFullscreen) {
        /* IE/Edge */
        elem.msRequestFullscreen();
    }
}
/* Close fullscreen */
//https://www.w3schools.com/howto/howto_js_fullscreen.asp
function closeFullscreen() {
    let elem = document.documentElement;
    if (document.exitFullscreen) {
        document.exitFullscreen();
    }
    else if (document.mozCancelFullScreen) {
        /* Firefox */
        document.mozCancelFullScreen();
    }
    else if (document.webkitExitFullscreen) {
        /* Chrome, Safari and Opera */
        document.webkitExitFullscreen();
    }
    else if (document.msExitFullscreen) {
        /* IE/Edge */
        document.msExitFullscreen();
    }
}
/**
 * 
 * @param {String} selector 
 * @returns null
 */
function NonSweetClick(selector) {
    if (IsSwalClose()) {
        $(selector).click()
    }
}
/**
 * 
 * @param {Optional[String]} msg 
 * @param {int} enter_sec 
 * @param {int} show_sec 
 * @param {Optional[int]} exit_sec 
 * @param {String} cls 
 * @returns throws a message to the user that not blockes input
 */
const throw_message = (msg, enter_sec = 1000, show_sec = 100, exit_sec = null, cls = null) =>
    $("<div></div>").addClass(
        `pop-up-message center nonselect${_.isString(cls) ? ' ' + cls : ''}`)
    .text(msg).appendTo("body")
    // enter
    .animate({
        opacity: '70%'
    }, enter_sec, function() {
        // keep the element amount of time
        let self = this;
        setTimeout(function() {
                exit_sec = isNaN(exit_sec) ? enter_sec : exit_sec;
                if (exit_sec > 0) {
                    $(self).animate({
                            opacity: '0'
                        },
                        exit_sec,
                        function() {
                            $(this).parent().remove(self);
                        });
                } else {
                    $(self).parent().remove(self);
                }
            },
            show_sec
        );
    });
class PalColor {
    constructor(r, g, b, name) {
        this.r = r;
        this.g = g;
        this.b = b;
        this.name = name;
    }
    /**
     * returns the 32-bit size int represent the reversed rgba of the color
     */
    get abgr() {
        return (0xFF000000 | this.r | this.g << 8 | this.b << 16) << 0;
    }
    css_format(alpha = 1) {
        return `rgba(${this.r}, ${this.g}, ${this.b}, ${alpha})`;
    }
}
class SimpleInterval {
    constructor(work, time) {
        this.work = work;
        this.__time = time;
        this.work_handler = null;
    }
    start() {
        this.work_handler = setInterval(this.work, this.__time);
    }
    stop() {
        clearInterval(this.work_handler)
        this.work_handler = null
    }
    safeStart() {
        if (_.isNull(this.work_handler)) {
            this.start()
            return true;
        }
        return false;
    }
    safeStop() {
        if (_.isNull(this.work_handler)) {
            return False
        } //else 
        this.stop();
        return true;
    }
    get isWorking() {
        return !_.isNull(this.work_handler);
    }
}
class CursorState {
    constructor(cursor, hide_pen) {
        this.cursor = cursor;
        this.hide_pen = hide_pen;
    }
    /**
     * @name equals
     * @param {CursorState} other_cursor 
     * @returns Boolean -> if the 2 cursors states are the same
     */
    equals(other_cursor) {
        //https://stackoverflow.com/a/1249554
        if (!(other_cursor instanceof CursorState)) {
            return false;
        }
        return (
            this.cursor == other_cursor.cursor &&
            this.hide_pen == other_cursor.hide_pen
        )
    }
}
const Colors = {
    white: new PalColor(0xFF, 0xFF, 0xFF, 'White'),
    black: new PalColor(0x00, 0x00, 0x00, 'Black'),
    gray: new PalColor(0x80, 0x80, 0x80, 'Gray'),
    silver: new PalColor(0xC0, 0xC0, 0xC0, 'Silver'),
    red: new PalColor(0xFF, 0x00, 0x00, 'Red'),
    pink: new PalColor(0xFF, 0xC0, 0xCB, 'Pink'),
    brown: new PalColor(0x8B, 0x45, 0x13, 'Brown'),
    orange: new PalColor(0xFF, 0xA5, 0x00, 'Orange'),
    olive: new PalColor(0x80, 0x80, 0x00, 'Olive'),
    yellow: new PalColor(0xFF, 0xFF, 0x00, 'Yellow'),
    green: new PalColor(0x00, 0x80, 0x00, 'Green'),
    lime: new PalColor(0x00, 0xFF, 0x00, 'Lime'),
    blue: new PalColor(0x00, 0x00, 0xFF, 'Blue'),
    aqua: new PalColor(0x00, 0xFF, 0xFF, 'Aqua'),
    purple: new PalColor(0x80, 0x00, 0x80, 'Purple'),
    magenta: new PalColor(0xFF, 0x00, 0xFF, 'Magenta'),
    colors: [],
    construct() {
        this.colors.push(this.white);
        this.colors.push(this.black);
        this.colors.push(this.gray);
        this.colors.push(this.silver);
        this.colors.push(this.red);
        this.colors.push(this.pink);
        this.colors.push(this.brown);
        this.colors.push(this.orange);
        this.colors.push(this.olive);
        this.colors.push(this.yellow);
        this.colors.push(this.green);
        this.colors.push(this.lime);
        this.colors.push(this.blue);
        this.colors.push(this.aqua);
        this.colors.push(this.purple);
        this.colors.push(this.magenta);
    },
    findAbgr(abgr) {
        for (let i = 0; i < this.colors.length; i++) {
            if (abgr == this.colors[i]) {
                return i;
            }
        }
        return -1;
    },
}
/*
function arrayBufferToBase64(buffer) {
    var binary = '';
    var bytes = [].slice.call(new Uint8Array(buffer));
    bytes.forEach((b) => binary += String.fromCharCode(b));
    return window.btoa(binary);
};
*/
const Cursors = {
    Pen: new CursorState('crosshair', false),
    Wait: new CursorState('not-allowed', false),
    grabbing: new CursorState('grabbing', true),
    FindMouse: new CursorState('wait', true)
    /*    Vertical: new CursorState('ns-resize', false),
        Horizontal: new CursorState('we-resize', false),
        LinearDown: new CursorState('nw-resize', false),
        LinearUp: new CursorState('ne-resize', false)*/
}
//https://stackoverflow.com/a/50248437
/*
const ImageImporter = {
    __urls:[
        'https://i.imgflip.com/10eahj.jpg',
        'https://aadityapurani.files.wordpress.com/2016/07/2.png'
    ],
    __images: [
    ],
    __getImageMime(url){
        if(url.endsWith('.jpg')){
            return 0;
        } else if((url.endsWith('.png'))){
            return 0;
        }
        return null;
    },
    __fetchImage(url){
        mime_type = this.__getImageMime(url);
        if(_.isNull(mime_type)){
            throw new Error('Mime image unvalid');
        }
        // else fetch
        //https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
        fetch(
            url,
            {
                method: 'GET',
                headers:{
                    'Content-Type': mime_type
                },
                referrerPolicy: 'no-referrer',
                cache: 'force-c
                ',
            })
            .then(response => response.blob())
            .then(images => {
                outside = URL.createObjectURL(images);
                console.log(images);
                this.__images.push(outside)
            })
         
    },
    construct(){
        this.__urls.forEach((url) => {
            this.__fetchImage(url);
        })
    }  
}
*/
const progress = {
    time: 0, // time when cooldown ends
    state: 0, // state of progress bar
    work: null, // handler of progress update interval
    current_min_time: null,
    construct() {
        let self = this;
        this.work = new SimpleInterval(function() {
            self.updateTimer()
        }, PROGRESS_COOLDOWN)
    },
    adjust_progress(seconds_left) {
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
    setTime(time) {
        // set time
        // handles starting the timer waiting
        this.time = Date.parse(time + ' UTC');
        // if current time is after end of cooldown
        if (this.time < getUTCTimestamp()) {
            $('prog-text').text('0:00'); // set textto 0
            $('#prog-fill').attr('state', 1); // prog-fill state is 9
            $('#time-prog').attr('state', 0); // time progress set to 1
            if (this.work.isWorking) { // stop work in case
                this.work.stop();
            }
        }
        else if (!this.work.isWorking) {
            this.current_min_time = 300;
            this.work.start()
            cursor.setPen();
        }
    },
    updateTimer() {
        // Updates the prorgess bar and timer each interval
        // Math.max the time until cooldown ends in ms, compare if positive (the time has not passed),
        // ceil to round up, I want to prevent the progress showing time up to that
        let seconds_left = Math.ceil(Math.max(this.time - getUTCTimestamp(),
            0) / 1000);
        // adjust progress
        if (this.current_min_time != seconds_left) {
            this.adjust_progress(seconds_left);
            // update current time
            this.current_min_time = seconds_left;
        }
        // close for cooldown 0
        if (seconds_left <= 0) {
            // clear Interval
            this.stopProgress();
        }
    },
    stopProgress() {
        this.work.stop();
        cursor.setPen();
    }
}
const query = {
    cx: DEFAULT_START_AXIS, // the x of the center pixel in the canvas on screen
    cy: DEFAULT_START_AXIS, // the y of the center pixel in the canvas on screen
    scale: DEFAULT_SCALE_MULTIPLAYER,
    __can_set_hash: HashChangeFlag.Enabled,
    // constructialize the query object
    construct() {
        // set window hash to be valid
        fragments = this.determineFragments();
        this.cx = fragments.x;
        this.cy = fragments.y;
        this.scale = fragments.scale;
    },
    disableUpdateHash() {
        this.__can_set_hash = HashChangeFlag.Disabled;
    },
    enableUpdateHash() {
        if (this.__can_set_hash != HashChangeFlag.Enabled) {
            if (this.__can_set_hash == HashChangeFlag.Needed) {
                this.__can_set_hash = HashChangeFlag.Enabled
                this.setHash()
            } else {
                this.__can_set_hash = HashChangeFlag.Enabled;
            }
        }
    },
    canSetHash() {
        return this.__can_set_hash == HashChangeFlag.Enabled
    },
    // the hash of the window
    get __path() {
        return `x=${this.cx}&y=${this.cy}&scale=${this.scale}`
    },
    // return string represent the hash of the page
    hash() {
        return `#${this.__path}`
    },
    // args string represent the args of the hash
    arguments() {
        return `?${this.__path}`
    },
    // validation check fo reach attributes
    is_valid_new_x(val) {
        return (!isNaN(val)) && is_valid_pos(val) && val != this.cx
    },
    is_valid_new_y(val) {
        return (!isNaN(val)) && is_valid_pos(val) && val != this.cy
    },
    is_valid_new_scale(val) {
        return (!isNaN(val)) && is_valid_scale(val) && val != this.scale
    },
    determineX() {
        // first get from arguments
        let x = window.location.search.match(reArgX);
        x = parseInt(getFirstIfAny(x))
        if ((!isNaN(x)) && is_valid_pos(x)) {
            return x;
        }
        // second get from hash
        x = window.location.hash.match(reHashX);
        x = parseInt(getFirstIfAny(x))
        if ((!isNaN(x)) && is_valid_pos(x)) {
            return x;
        }
        // else search for value in body
        x = parseInt($('body').attr('x'))
        if ((!isNaN(x)) && is_valid_pos(x)) {
            return x;
        }
        return DEFAULT_START_AXIS;
    },
    determineY() {
        // first get from arguments
        let y = window.location.search.match(reArgY);
        y = parseInt(getFirstIfAny(y))
        if ((!isNaN(y)) && is_valid_pos(y)) {
            return y;
        }
        // second get from hash
        y = window.location.hash.match(reHashY);
        y = parseInt(getFirstIfAny(y))
        if ((!isNaN(y)) && is_valid_pos(y)) {
            return y;
        }
        // else search for value in body
        y = parseInt($('body').attr('y'))
        if ((!isNaN(y)) && is_valid_pos(y)) {
            return y;
        }
        return DEFAULT_START_AXIS;
    },
    determineScale() {
        // first get from arguments
        let scale = window.location.search.match(reArgScale);
        scale = parseFloat(getFirstIfAny(scale))
        if ((!isNaN(scale)) && is_valid_scale(scale)) {
            return scale;
        }
        // second get from hash
        scale = window.location.hash.match(reHashScale);
        scale = parseFloat(getFirstIfAny(scale))
        if ((!isNaN(scale)) && is_valid_scale(scale)) {
            return scale;
        }
        // else search for value in body
        scale = parseFloat($('body').attr('scale'))
        if ((!isNaN(scale)) && is_valid_scale(scale)) {
            return scale;
        }
        return SIMPLE_UNZOOM_LEVEL;
    },
    // use regex to get fragments
    determineFragments() {
        return {
            x: this.determineX(),
            y: this.determineY(),
            scale: this.determineScale()
        };
    },
    // set x and
    // level 2 - set query
    setCenter(x = undefined, y = undefined, to_update = true) {
        let flag = false;
        x = this.scale >= 1 ? Math.round(x) : CANVAS_SIZE / 2;
        y = this.scale >= 1 ? Math.round(y) : CANVAS_SIZE / 2;
        if (this.is_valid_new_x(x)) {
            flag = true;
            this.cx = x;
        }
        if (this.is_valid_new_y(y)) {
            flag = true;
            this.cy = y;
        }
        if (to_update && flag) {
            board.centerPos();
            this.setHash();
        }
        return flag;
    },
    // level 2 set query
    setScale(scale, to_update = true) {
        if (this.is_valid_new_scale(scale)) {
            this.scale = scale;
            if (1 > this.scale) {
                this.setCenter(CANVAS_SIZE / 2, CANVAS_SIZE / 2, false);
            }
            if (to_update) {
                board.updateZoom();
            }
            this.setHash()
        }
    },
    // level 1 interaction of query change
    refreshFragments(to_update) {
        /*  refreshFragments(bool) -> void
         *  refresh the query object by the current hash values if they are valid
         */
        let frags = this.determineFragments();
        this.setCenter(this.x, this.y, to_update);
        if (this.is_valid_new_scale(frags.scale)) {
            this.scale = frags.scale;
            if (to_update) {
                board.updateZoom();
            }
        } else {
            this.setHash();
        }
    },
    // set the window.loaction.hash to the query hash value
    // level 3
    setHash() {
        //  update location
        // first tried to update event set
        // now lets try using setTimeout
        this.__can_set_hash = MaskHashChangeFlag(this.__can_set_hash)
        if (this.canSetHash() && location.hash != this.hash()) {
            // change hash without triggering events
            // https://stackoverflow.com/a/5414951
            history.replaceState(null, null, document.location.pathname +
                this.hash());
            //window.location.hash = this.hash;  
        }
    }
}
const cursor = {
    last_cursor_non_forced: null,
    current_cursor: null,
    force_cursor: null,
    /**
     * @param {CursorState} other_cursor 
     */
    setCursor(other_cursor) {
        // update last cursor
        if (other_cursor instanceof CursorState) {
            this.last_cursor_non_forced = other_cursor;
        }
        let cursor = this.force_cursor || this.last_cursor_non_forced;
        if (_.isNull(this.current_cursor) || !this.current_cursor.equals(cursor)) {
            if ((!this.current_cursor) || cursor.cursor != this.current_cursor.cursor) {
                board.canvas.css('cursor', cursor.cursor);
            }
            if (cursor.hide_pen) {
                pen.disable();
            }
            else {
                pen.enable();
            }
            this.current_cursor = cursor;
        }
    },
    setPen() {
        this.setCursor(progress.work.isWorking || lock_object.locked ? Cursors.Wait : Cursors.Pen)
    },
    grab() {
        this.setCursor(Cursors.grabbing);
    },
    lockCursor(cursor) {
        this.force_cursor = cursor;
        this.setCursor();
    },
    releaseCursor(cursor_state) {
        if (cursor_state.equals(this.force_cursor)) {
            this.force_cursor = null;
            this.setCursor()
        }
    }
    /*
    __getDirCursor(dx, dy){
        // x axis index = 0
        // y axis index = 1
        if(dx == 0 && dy == 0){
            return null;
        }
        if(dx == 0){
            return Cursors.Horizontal
        } else if(dy == 0){
            return Cursors.Vertical;
        } else if(dy != dx) {
            return Cursors.LinearUp;
        } // else
        return Cursors.LinearDown;
    },
    setDirCursor(dir){
        let cur = this.__getDirCursor(dir[0], dir[1]);
        if(_.isNull(cur)){
           this.setPen();
        } else {
            this.setCursor(cur);
        }
    }*/
}
const pen = {
    x: null,
    y: null,
    __color: null,
    last_mouse_pos: null,
    // in keyboard state, the pen should point at the center of the screen
    force_center: true,
    __disable: false,
    cursor_style: 'default',
    construct() {
        let color_button = $('.colorButton[picked="1"]').first()
        if (!color_button[0]) {
            color_button = $('.colorButton').first(); // black button
        }
        this.setColorButton(color_button)
    },
    disable() {
        if (!this.__disable) {
            this.__disable = true;
            board.drawBoard();
        }
    },
    enable() {
        if (this.__disable) {
            this.__disable = false;
            board.drawBoard();
        }
    },
    getMouseOffset(e) {
        /*
            if(pen.force_center){
                return [
                    innerWidth/(2*query.scale),
                    innerHeight/(2*query.scale)
                ];
        */
        if (e) {
            // set last_mouse_pos
            this.last_mouse_pos = [e.pageX, e.pageY]
        }
        return this.last_mouse_pos;
    },
    updateOffset(e) {
        /* finds the pen current position
         min pixel on screen + start of page / scale= position of mouse  */
        let pos = null;
        if (this.force_center) {
            pos = {
                x: Math.floor(board.x + board.canvas[0].width / 2 / query.scale),
                y: Math.floor(board.y + board.canvas[0].height / 2 / query.scale)
            } // center
        }
        else {
            // clear pos when both values aren't good
            let mouse_offset = this.getMouseOffset(e);
            if (_.isNull(mouse_offset) || _.some(mouse_offset, _.isNull)) {
                return;
            }
            pos = {
                x: Math.floor(board.x + mouse_offset[0] / query.scale),
                y: Math.floor(board.y + mouse_offset[1] / query.scale)
            }
        }
        if (_.isNull(pos) || (!is_valid_pos(pos.x)) || (!is_valid_pos(pos.y))) {
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
    clearPos() {
        // when out of board
        this.x = this.y = -1;
        board.updateCoords();
        board.drawBoard();
    },
    setPenPos(e) {
        // update position and end use of keyboard state center
        this.force_center = false;
        this.updateOffset(e);
    },
    setCenterPos() {
        cursor.setPen();
        this.force_center = true;
        this.updateOffset();
    },
    setColorButton(button) {
		console.log(button)
		this.color = parseInt(button.attr('value'));
        $('.colorButton[picked="1"]').attr('picked', '0');
        button.attr('picked', '1');
    },
    get hasColor() {
        return (!isNaN(this.__color)) && this.__color > 0 && this.__color < 16;
    },
    // color getter ans setter
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
    isAtBoard() {
        return this.x != -1 || this.y != -1
    },
    canDrawPen() {
        return (!this.__disable) && this.hasColor && this.isAtBoard()
    },
    setPixel() {
        if(!sock.connected) {
            Swal.fire({
                title: 'Server Not Found',
                imageHeight: 300,
                imageUrl:'https://i.chzbgr.com/full/570936064/hF75ECDD4/error-404-server-not-found',
                imageAlt:'Server Not Found and Also this image, maybe you out of internet',
                text:'The Server Cannot be Found, if you wait a little it might be found',
                confirmButtonText: 'To Waiting'
            })
        }
        if (!board.is_ready) {
            Swal.fire({
                title: 'Wait for the board',
                text: 'Wait for the board to load before doing something'
            });
        }
        else if (progress.work.isWorking) {
            Swal.fire({
                title: 'You have 2 wait',
                imageUrl: 'https://aadityapurani.files.wordpress.com/2016/07/2.png',
                imageHeight: 300,
                imageAlt: 'wow that was rude',
                text: 'Wait for your cooldown to end'
            });
        }
        else if (lock_object.locked) {
            Swal.fire({
                title: 'Canvas is closed',
                imageUrl: 'https://img.memecdn.com/door-lock_o_2688511.jpg',
                imageHeight: 250,
                imageAlt: 'SocialPainterDash canvas is currently closed',
                text: 'Wait an admin will open it up',
                confirmButtonText: 'To Waiting'
            });
        }
        else if (!this.hasColor) {
            Swal.fire({
                icon: 'warning',
                title: 'Select Color',
                text: 'Pless select color from the table',
            });
        }
        else {
            sock.emit('set-board', {
                'color': this.__color,
                'x': this.x,
                'y': this.y,
            }, callback = (value) => {
                if (_.isUndefined(value) || value == 'undefined') {
                    return;
                }
                // else it must be json
                data = JSON.parse(value);
                if (data.code == 'lock' && data.value == 'true') {
                    lock_object.lock()
                } else if (data.code == 'set-time') {
                    progress.setTime(data.value)
                }
            });
        }
    }
}
const lock_object = {
    __locked: false,
    get locked() {
        return this.__locked;
    },
    lock() {
        this.__locked = true;
        $('#lock-colors').attr('lock', 1);
    },
    unlock() {
        this.__locked = false;
        $('#lock-colors').attr('lock', 0);
    }
}
const board = {
    imgCanvas: null,
    ctx_image: null,
    buffer: null,
    x: 0,
    y: 0,
    drag: {
        active: false,
        startX: 0,
        startY: 0,
        dragX: 0,
        dragY: 0
    },
    canvas: null,
    needs_draw: false,
    move_vector: [0, 0],
    key_move_interval: null,
    ctx: null,
    pixelQueue: null,
    buildBoard: null,
    construct() {
        this.canvas = $('#board');
        this.ctx = this.canvas[0].getContext('2d');
        this.canvas.attr('alpha', 0);
        this.imgCanvas = document.createElement('canvas');
        this.imgCanvas.width = CANVAS_SIZE;
        this.imgCanvas.height = CANVAS_SIZE;
        this.ctx_image = this.imgCanvas.getContext('2d');
        this.reset_board_build()
        this.updateZoom(); // also centers
    },
    get is_ready() {
        /**
         * checked if the board is ready
         */
        return _.isNull(this.pixelQueue);
    },
    reset_board_build() {
        /**
         * reset values for board build
         */
        this.buildBoard = _.once(this.__buildBoard);
        this.pixelQueue = [];
    },
    // level 1
    // interaction of key press
    startKeyMoveLoop() {
        board.moveBoard(this.move_vector[0], this.move_vector[1])
        if (_.isNull(this.key_move_interval)) {
            query.disableUpdateHash();
            this.key_move_interval = setInterval(() => {
                board.moveBoard(this.move_vector[0], this
                    .move_vector[1]);
            }, 100);
        }
    },
    // level 1
    addMovement(dir) {
        dir.set = true;
        this.move_vector[0] += dir.dir[0]
        this.move_vector[1] += dir.dir[1];
        //cursor.setDirCursor(this.move_vector)
        this.startKeyMoveLoop();
    },
    // level 1
    subMovement(dir) {
        dir.set = false
        this.move_vector[0] -= dir.dir[0];
        this.move_vector[1] -= dir.dir[1];
        //cursor.setDirCursor(this.move_vector);
        if (this.move_vector[0] == 0 && this.move_vector[1] == 0) {
            clearInterval(this.key_move_interval)
            query.enableUpdateHash();
            this.key_move_interval = null;
        }
    },
    //uffer on chrome takes ~1552 ms -- even less
    __buildBoard(buffer) {
        let image_data = new ImageData(CANVAS_SIZE, CANVAS_SIZE);
        let image_buffer = new Uint32Array(image_data.data.buffer);
        buffer.forEach(function(val, index) {
            // first version of putting data, looping over the image buffer array and not of buffer of message
            //var bit = buffer[Math.floor(index/2)];
            //self.buffer[index] = reverseRGBA(COLORS[index % 2 == 0 ? bit % 16 : bit >> 4]);
            image_buffer[index * 2] = Colors.colors[val % 16].abgr; // small int
            image_buffer[index * 2 + 1] = Colors.colors[Math.floor(val / 16)].abgr; // big int
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
        // x: int (0 < x < 1000)
        // y: int (0 < x < 1000)
        if (color_idx < 0 || color_idx > 15) {
            // swal event
        }
        if (!(is_valid_pos(x) && is_valid_pos(y))) {
            throw_message('given position of point isnt valid')
        }
        color = Colors.colors[color_idx].css_format();
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
    },
    // empty the pixel queen
    beforeFirstDraw() {
        while (this.pixelQueue.length != 0) {
            let obj = this.pixelQueue.shift(); // remove
            this.__setAt(obj.x, obj.y, obj.color);
        }
        this.pixelQueue = null;
        this.drawBoard();
    },
    /*
        findPos: function() {
          var curleft = 0, curtop = 0; obj = this.canvas;
          if (obj.offsetParent) {
            do {
                curleft += obj.offsetLeft;
                curtop += obj.offsetTop;
            } while (obj = obj.offsetParent);
            rect = this.canvas.getBoundingClientRect();
            return { x: curleft, y: curtop };
        }
        return undefined;
        },*/
    /*getCoords: function (e) {
        return {
            x: Math.floor((e.pageX - this.mover[0].getClientRects()[0].left) / board.scale),
            y: Math.floor((e.pageY - this.mover[0].getClientRects()[0].top) / board.scale)-1 // because reasons, during debugging it come to this;
        };
    },*/
    get windowBounding() {
        return CANVAS_SIZE * this.scale / 2;
    },
    // sets the board position
    // level 3
    centerPos() {
        // center axis - (window_axis_size / 2 / query.scale)
        this.x = Math.floor(query.cx - board.canvas[0].width / 2 / query
            .scale) //( query.cx - innerWidth/2)/query.scale;
        this.y = Math.floor(query.cy - board.canvas[0].height / 2 / query
            .scale) // (query.cy - innerHeight/2)/query.scale;
        pen.updateOffset()
        board.drawBoard();
    },
    // level 3
    setCanvasZoom() {
        //https://www.html5rocks.com/en/tutorials/canvas/hidpi/
        let width = innerWidth * devicePixelRatio;
        let height = innerHeight * devicePixelRatio;
        this.canvas[0].width = width;
        this.canvas[0].height = height;
        // found to solve this
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.centerPos();
        this.drawBoard();
    },
    // level 3
    updateZoom() {
        this.setZoomStyle()
        this.setCanvasZoom();
        pen.updateOffset();
    },
    setZoomStyle() {
        let zoom_button = $('#zoom-button')
        if (query.scale >= 25) {
            zoom_button.children('span').addClass('fa-search-minus')
                .removeClass('fa-search-plus');
            zoom_button.css('cursor', 'zoom-out');
        }
        else {
            zoom_button.children('span').addClass('fa-search-plus')
                .removeClass('fa-search-minus');
            zoom_button.css('cursor', 'zoom-in');
        }
    },
    get step() {
        // the scale is inproportion to the step size
        return MIN_STEP_SIZE * MAX_SCALE / query.scale;
    },
    // level 1
    moveBoard(dx, dy) {
        /*      let x = this.keep_inside_border(this.real_x, dir[DIR_INDEX_XNORMAL]*this.step*this.scale, rect.left, rect.right)/this.scale;
              let y = this.keep_inside_border(this.real_y, dir[DIR_INDEX_YNORMAL]*this.step*this.scale, rect.top, rect.bottom)/this.scale;
              console.log(x, y);
        */
        query.setCenter(
            clamp(query.cx + dx * this.step, CANVAS_SIZE, 0),
            clamp(query.cy + dy * this.step, CANVAS_SIZE, 0)
        );
    },
    // level 1
    centerOn(x, y) {
        x = isNaN(x) ? query.cx : clamp(x, CANVAS_SIZE, 0);
        y = isNaN(y) ? query.cy : clamp(y, CANVAS_SIZE, 0);
        query.setCenter(x, y);
    },
    // level 3 in half
    updateCoords() {
        // not (A or B) == (not A) and (not B)
        if ($('#coordinates').is(':hover')) {
            $('#coordinate-slicer').text('copy')
            $('#coordinateX').text('');
            $('#coordinateY').text('');
        }
        else if (!board.drag.active) {
            $('#coordinate-slicer').text(pen.isAtBoard() ? ',' :
                'None');
            $('#coordinateX').text(pen.isAtBoard() ? pen.x : '');
            $('#coordinateY').text(pen.isAtBoard() ? pen.y : '');
        }
    },
    drawBoard() {
        if (board.needs_draw || !board.is_ready) {
            return;
        }
        this.needs_draw = true;
        requestAnimationFrame(
            () => { // 1-5 millisecond call, for all animation
                // it seems the average time of 5 operations is 0.23404487173814767 milliseconds
                //t = performance.now();
                this.needs_draw = false;
                this.ctx.fillStyle = BACKGROUND_COLOR
                this.ctx.fillRect(0, 0,
                    // for the scale == 0.5 scenerio
                    this.canvas[0].width, this.canvas[0].height);
                this.ctx.save()
                this.ctx.imageSmoothingEnabled = false;
                this.ctx.scale(query.scale, query.scale)
                this.ctx.translate(-this.x, -this.y);
                this.ctx.drawImage(this.imgCanvas, 0, 0);
                if (pen.canDrawPen()) {
                    this.ctx.fillStyle = Colors.colors[pen.color]
                        .css_format(0.6);
                    this.ctx.fillRect(pen.x, pen.y, 1, 1);
                }
                this.ctx.restore(); // return to default position
                //performance_arr.push(performance.now()-t)
            });
    }
};
//const performance_arr = []
const sock = io('/paint', {
    autoConnect: false,
    transports: ['websocket'] // or [ 'websocket', 'polling' ], which is the same thing
});
$(document).ready(function() {
    sock.on('connect', function() {
        sock.emit('get-starter', (data) => {
            progress.setTime(data.time)
            board.buildBoard(new Uint8Array(data.board));
            if (data.lock) {
                lock_object.lock();
            }
        });
    })
    sock.connect()
    Colors.construct();
    query.construct();
    progress.construct();
    board.construct();
    pen.construct();
    query.setHash();
    sock.on('set-board', (x, y, color_idx) => board.setAt(x, y, color_idx));
    // Lost connection
    sock.on('disconnect', () => {
        board.reset_board_build();
        Swal.fire({
            icon: 'error',
            title: 'Lost connection with the server',
            text: 'Server Lost Connection',
        });
    });
    // Connection on
    sock.on('change-lock-state', (is_paused) => {
        // if data is true
        if (is_paused) {
            // unpause code
            lock_object.lock();
        } else {
            // pause code
            lock_object.unlock();
        }
    });
    sock.on('reconnect', () => {
        Swal.fire({
            icon: 'success',
            title: 'Reconnected to the server',
            text: 'Server Connection returned',
        })
    });
    $('#coordinates').hover(function() {
        board.updateCoords();
    }, function() {
        board.updateCoords();
    });
    // set color
    board.canvas.mousemove((event) => {
        pen.setPenPos(event);
    }).mouseleave(() => pen.clearPos()).bind('mousewheel', (e) => {
        e.preventDefault();
        query.setScale(clamp(query.scale + Math.sign(e
                .originalEvent.wheelDelta) * 1,
            MAX_SCALE, MIN_SCALE));
    })[0].addEventListener('dblclick', (
        event) => { // for not breaking the 
        // jquery dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        pen.setPenPos(event);
        cursor.setPen();
        pen.setPixel();
    });
    board.canvas.mousedown(function(e) {
        board.drag.dragX = e.pageX;
        board.drag.dragY = e.pageY;
        board.drag.startX = query.cx;
        board.drag.startY = query.cy;
        board.drag.active = true;
        query.disableUpdateHash();
        // change cursor 100 seconds if don't move
    }).mouseenter(function(e) {
        cursor.setPen();
    })
    $(document).mousemove(function(e) {
        if (board.drag.active) {
            // center board
            cursor.grab();
            board.centerOn(
                Math.floor(board.drag.startX + (board.drag.dragX - e.pageX) / query.scale),
                Math.floor(board.drag.startY + (board.drag.dragY - e.pageY) / query.scale)
            );
        }
    }).mouseup(() => {
        board.drag.active = false;
        cursor.setPen();
        query.enableUpdateHash();
    })
    $(document).keypress(function(e) {
        // first check direction
        // https://stackoverflow.com/a/9310900
        switch (e.code) {
            case 'KeyX': {
                $('#toggle-toolbox-button').click();
                break;
            }
            case 'KeyC': {
                let button = $(".colorButton[picked='1']").first();
                // if any of the is undefiend - reset
                if (_.isUndefined(button[0]) || _.isUndefined(button.next()[0])) {
                    let button = $(".colorButton").first()
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
                if (pen.force_center && IsSwalClose()) {
                    pen.setPixel();
                }
                else if (!pen.force_center) {
                    pen.setCenterPos()
                }
                break;
            }
            case 'KeyG': {
                cursor.lockCursor(Cursors.FindMouse);
                break;
            }
            case 'KeyF': {
                NonSweetClick('#screen-button')
                break;
            }
            default: {
                break;
            }
        }
        if (e.originalEvent.shiftKey) {
            if (e.originalEvent.key == '+') // key for plus
            {
                // option 0.5
                console.log(query.scale >= 1, query.scale)
                query.setScale(query.scale >= 1 ? query.scale + 1 : 1);
            }
            else if (e.originalEvent.key == '_') { // key for minus
                // option 0.5
                query.setScale(query.scale > 1 ? query.scale - 1 : MIN_SCALE);
            }
        }
    }).keydown((e) => {
        key = (e || window.event).key;
        let dir = _.findWhere(DIRECTION_MAP, {
            key: key
        })
        if ((!_.isUndefined(dir)) && !dir.set) {
            board.addMovement(dir);
        }
    }).keyup((e) => {
        let key = (e || window.event).key;
        let dir = _.findWhere(DIRECTION_MAP, {
            key: key
        })
        if ((!_.isUndefined(dir)) && dir.set) {
            board.subMovement(dir);
        }
        else if (key == 'Home') {
            NonSweetClick('#home-button');
        }
        else if (key == 'g') {
            cursor.releaseCursor(Cursors.FindMouse)
        } else if (key == 'Escape') {
            // prevent collison with swal ESCAPE
            NonSweetClick('#logout-button');
        }
    });
    // change toggle button
    $('#toggle-toolbox-button').click(function(e) {
        e.preventDefault();
        let toolbox = $('#toolbox')[0];
        // fade icons and move the toolbox down by setting its hide attribute to 1
        if (toolbox.getAttribute('hide') == 0) {
            $('.icon-button').fadeOut(500)
            toolbox.setAttribute('hide', 1)
        }
        else {
            // reveal icons
            $('.icon-button').fadeIn(500)
            toolbox.setAttribute('hide', 0)
        }
    });
    // hash change
    $(window).bind('hashchange', function(e) {
        if (window.location.hash != query.hash) {
            query.refreshFragments();
        }
    });
    // copy coords - https://stackoverflow.com/a/37449115
    let clipboard = new ClipboardJS('#coordinates', {
        text: function() {
            return window.location.origin + window.location
                .pathname + query.arguments();
        }
    });
    clipboard.on('success', function() {
        throw_message('Copy Success');
    })
    clipboard.on('error', function() {
        throw_message('Copy Error');
    })
    // change zoom level
    $('#zoom-button').click(function() {
        query.setScale($(this).children().hasClass('fa-search-minus') ? SIMPLE_UNZOOM_LEVEL : SIMPLE_ZOOM_LEVEL)
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
		$(this).css('background-color', Colors.colors[parseInt($(this).attr('value'))].css_format()); // set colors
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
    // set color button
    $(window).resize((e) => {
        board.setCanvasZoom();
    })
});
/**
 * list to do
 * --add center mouse button move.
 * potentional:
 * --work on mouse moving bug with sweet-alert (save position of mouse event when stops hover)
 */