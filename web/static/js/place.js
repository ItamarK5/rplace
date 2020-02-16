/*
    level of functions
    1) the interaction
    2) setting the query
    3) a function that affect the board as result of change in query
*/

const BACKGROUND_COLOR = '#777777'
const CANVAS_SIZE = 1000;
const ESC_KEY_CODE = 27;
const HOME_KEY_CODE = 36;
const MIN_STEP_SIZE = 1;
const MIN_SCALE = 0.5;
const MAX_SCALE = 50;
const DRAW_COOLDOWN = 60;

const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;
const reHashScale = /(?<=(^#|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;

const reArgX = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;
const reArgY = /(?<=(^\?|.+&)x=)\d+(?=&|$)/i;
const reArgScale = /(?<=(^\?|.+&)scale=)(\d{1,2}|0\.5)(?=&|$)/i;

//const reHash = /(?<=(?:^#|.+&))([\w|\d]+)=([\w|\d]+)(?=&|$)/i
const PEN_CURSOR = 'crosshair'
const MOVE_CURSOR = 'move'
const NONE_CURSOR = 'none'

const CURSOR_DIRECTION = [
    'nw-resize', 'ns-resize', 'ne-resize',
    'nw-resize', null, 'nw-resiz'
]

const DIRECTION_MAP = [
    {key:37, dir:[-1,  0], set:false}, // left
    {key:39, dir:[ 1,  0], set:false}, // right
    {key:38, dir:[ 0, -1], set:false}, // up
    {key:40, dir:[ 0,  1], set:false}  // down
];

const SIMPLE_ZOOM_LEVEL = 40;
const SIMPLE_UNZOOM_LEVEL = 4;
const HIDDEN_BUTTON_OPACITY = .2;
const VIEW_BUTTON_OPACITY = 1.0;


const getOffset = (x, y) => (y * CANVAS_SIZE) + x;
const getFirstIfAny = (group) => _.isNull(group) ? null : group[0]
const clamp = (v, max, min) => Math.max(min, Math.min(v, max));
const is_valid_scale = (scale) => MIN_SCALE <= scale && scale <= MAX_SCALE;
const is_valid_pos = (v) => 0 <= v && v < CANVAS_SIZE;
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

//https://pietschsoft.com/post/2008/01/15/javascript-inttryparse-equivalent
/*
unused
function TryParseInt(str, defaultValue) {
    let retValue = defaultValue;
    if(!_.isNull(str)) {
        if(str.length > 0) {
            if (!isNaN(str)) {
                retValue = parseInt(str);
            }
        }
    }
    return retValue;
}
*/

const throw_message = (msg, speed = 1000, keep_speed = 100, exit_speed = null, cls = null) =>
    $("<div></div>")
        .addClass(`pop-up-message center nonselect${_.isString(cls) ? ' ' + cls : ''}`)
        .text(msg)
        .appendTo("body")
        // enter
        .animate({ opacity: '70%' }, speed, function () {
            // keep the element amount of time
            let self = this;
            setTimeout(function () {
                let exit_sp = _.isNull(exit_speed) ? speed : exit_speed;
                if (exit_sp > 0) {
                    $(self).animate({ opacity: '0' }, exit_sp, function () {
                        $(this).parent().remove(self);
                    });
                } else {
                    $(self).parent().remove(self);
                }
            }, keep_speed);
        });
    
class PalColor {
    constructor(r, g, b, name) {
        this.r = r;
        this.g = g;
        this.b = b;
        this.name = name;
    }
    get abgr() {
        return (0xFF000000 | this.r | this.g << 8 | this.b << 16) << 0;
    }
    css_format(alpha=1) {
        return `rgba(${this.r}, ${this.g}, ${this.b}, ${alpha})`;
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
    init: function () {
        this.colors.push(this.white);   this.colors.push(this.black);   this.colors.push(this.gray);    this.colors.push(this.silver);
        this.colors.push(this.red);     this.colors.push(this.pink);    this.colors.push(this.brown);   this.colors.push(this.orange);
        this.colors.push(this.olive);   this.colors.push(this.yellow);  this.colors.push(this.green);   this.colors.push(this.lime);
        this.colors.push(this.blue);    this.colors.push(this.aqua);    this.colors.push(this.purple);  this.colors.push(this.magenta);
    },
    findAbgr: function (abgr) {
        for (let i = 0; i < this.colors.length; i++) { if (abgr == this.colors[i]) { return i; } }
        return -1;
    },
    clr: function (idx) { return this.colors[idx]; }
}

let progress = {
    time: 0,        // time when cooldown ends
    state: 0,       // state of progress bar
    work: null,  // handler of progress update interval
    current_min_time:null,
    adjust_progress(seconds_left) {  
        // adjust the progress bar and time display by the number of seconds left
        $('#prog-text').text([
            (Math.floor(seconds_left / 60)).toString(),
            (seconds_left % 60).toString().padStart(2, '0')
        ].join(':'))
        // update progress fill
        // update area colored
        $('#prog-fill').css('width', (100 - (seconds_left / DRAW_COOLDOWN)*100) + "%");        
        // 1 if time less then halve the number of seconds 
        this.state = Math.ceil(seconds_left * 2 /DRAW_COOLDOWN);
        $('#time-prog').attr('state', this.state);        
    },
    set_time(time) {
        // set time
        // handles starting the timer waiting
        let self = this;
        self.time = Date.parse(time + ' UTC');
        if(self.timestamp < getUTCTimestamp()) {
            $('prog-text').text('0:00');
            $('#prog-fill').state = 1;
            $('#time-prog').attr('state', 0);
            if(_.isNull(self.work)){
                clearInterval(self.work);
            }
        } else if (_.isNull(self.work)) {
            self.is_working = true;
            self.work = setInterval(function () { self.updateTimer() }, 50);
       }
    },
    updateTimer() {
        // Updates the prorgess bar and timer each interval
        // Math.max the time until cooldown ends in ms, compare if positive (the time has not passed),
        // ceil to round up, I want to prevent the progress showing time up to that
        let seconds_left = Math.ceil(Math.max(this.time - getUTCTimestamp(), 0) / 1000);
        // adjust progress
        if (this.current_min_time != seconds_left){
            this.adjust_progress(seconds_left);
            // update current time
            this.current_min_time = seconds_left;
        }
        let self = this;
        // close for cooldown 0
        if (seconds_left <= 0) {
            // clear Interval
            clearInterval(self.work);
            self.work = null;
            self.current_min_time = 300;
        }       
    }
}


const query = {
    x: 500,        // the x of the center pixel in the canvas on screen
    y: 500,        // the y of the center pixel in the canvas on screen
    scale: 4,
    // initialize the 
    init() {
        // replace default position by fragments
        let is_any_frag_unvalid = false;
        // x
        _.pairs(this.fragments()).forEach((frag, idx) => {
            let key = frag[0]; let val = frag[1];
            if(_.isNull(val)){ return; /* return breaks loop operation */ }
            switch(key){
                case('x'):{
                    if(this.is_valid_new_x(val)){
                        this.x = Math.round(val);            
                    } else {is_any_frag_unvalid = true;}
                    break;
                }
                case('y'):{
                    if(this.is_valid_new_y(val)){
                        this.y = Math.round(val);            
                    } else {is_any_frag_unvalid = true;}            
                    break;
                }
                case('scale'): {
                    if (this.is_valid_new_scale(val)) {
                        this.scale = val
                    } else {is_any_frag_unvalid = true;}
                    break;
                }
            }
        })
        // if didn't refresh, update page
        if (is_any_frag_unvalid){ this.set_window_hash() }
    },
    // the hash of the window
    get __path() {
        return `x=${this.x}&y=${this.y}&scale=${this.scale}`
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
    is_valid_new_x(val) {return (!isNaN(val)) && is_valid_pos(val) && val != this.x },
    is_valid_new_y(val) {return (!isNaN(val)) && is_valid_pos(val) && val != this.y },
    is_valid_new_scale(val) {return (!isNaN(val)) && is_valid_scale(val) && val != this.scale },
    // use regex to get fragments
    fragments() {
        return {
            // first checks the hash if there are null, check the location
            x: parseInt(getFirstIfAny(window.location.hash.match(reHashX) || window.location.search.match(reArgX))),
            y: parseInt(getFirstIfAny(window.location.hash.match(reHashY) || window.location.search.match(reArgY))),
            scale: parseFloat(getFirstIfAny(window.location.hash.match(reHashScale) || window.location.search.match(reArgScale)))
        };
    },
    // set x and
    // level 2 - set query
    setCenter(x = undefined, y = undefined, to_update = true) {
        let flag = false;
        if(this.scale >= 1){
            x = Math.round(x);
            y = Math.round(y);    
        } else {x = 500; y=500;}
        if (this.is_valid_new_x(x)) { flag = true; this.x = x; }
        if (this.is_valid_new_y(y)) { flag = true; this.y = y; }
        if (to_update && flag) { board.centerPos(); this.set_window_hash() }
        return flag;
    },
    // level 2 set query
    setScale(scale, to_update = true) {
        if(this.is_valid_new_scale(scale)){
            this.scale = scale;
            if(1 > this.scale) {
                this.setCenter(CANVAS_SIZE/2, CANVAS_SIZE/2, false);
            }
            if(to_update){
                board.updateZoom();
            }
            this.set_window_hash()
        }
    },
    // level 1 interaction of query change
    refresh_fragments(to_update) {
        /*  refresh_fragments(bool) -> void
         *  refresh the query object by the current hash values if they are valid
         */
        let frags = this.fragments();
        if ((!isNaN(frags.x)) || (!isNaN(frags.y))) {
            this.setCenter(parseInt(frags.x), parseInt(frags.y), to_update);
        }
        /// update scale
        if (isNaN(frags.scale) && this.is_valid_new_scale(parseFloat(frags.scale))) {
            this.scale = this.scale;
            if (to_update) {
                board.updateZoom()
            }
        }
    },
    // set the window.loaction.hash to the query hash value
    // level 3
    set_window_hash() {
        //  update location
        if (window.location.hash != this.hash()) {
            // change hash without triggering events
            history.replaceState(null, null, document.location.pathname  + this.hash());
            //window.location.hash = this.hash;
        }
    }
}


const pen = {
    x:null, y:null, color:null,
    last_mouse_pos:null,
    // in keyboard state, the pen should point at the center of the screen
    force_center:true,
    __disable:false,
    cursor_style:'default',
    init() {
        this.color = $('.colorButton').index('[state="1"]');
    },
    set_cursor(cursor){
        board.canvas.css('cursor', cursor);
        this.__disable = cursor != PEN_CURSOR;
        if(this.__disable != cursor != PEN_CURSOR){
            this.__disable = cursor != PEN_CURSOR
            board.drawBoard();
        }
    },
    getMouseOffset(e){
        /*
            if(pen.force_center){
                return [
                    innerWidth/(2*query.scale),
                    innerHeight/(2*query.scale)
                ];
        */
        if(e) {
            // set last_mouse_pos
            this.last_mouse_pos = [e.pageX, e.pageY]
        }
        return this.last_mouse_pos;
    },
    updateOffset(e) {
        /* finds the pen current position
         min pixel on screen + start of page / scale= position of mousee  */
         let pos = null;
        if(this.force_center){
            pos = {x:query.x, y:query.y}   // center
        } else {
            // clear pos when both values arent good
            let mouse_offset = this.getMouseOffset(e);
            if (_.isNull(mouse_offset) || _.some(mouse_offset, _.isNull)){return;}
            pos = {
                x: Math.floor(board.x+mouse_offset[0]/query.scale),
                y: Math.floor(board.y+mouse_offset[1]/query.scale)
            }
        }
        if (_.isNull(pos) || (!is_valid_pos(pos.x)) || !is_valid_pos(pos.y)) {
            this.clearPos(); // set values to -1
        // but if not, update if the values are different
        } else if(pos.x != this.x || pos.y != this.y){
            this.x = pos.x;
            this.y = pos.y;
            board.drawBoard();
            board.updateCoords();
        }
    },
    clearPos(){
        // when entered outofboard
        this.x = this.y = -1;
        board.updateCoords();
        board.drawBoard();
    }, 
    setMousePos(e){
        // update position and end use of keyboard state center
        this.force_center = false;
        this.updateOffset(e);
    },
    setCenterPos(){        
        this.force_center = true;
        this.updateOffset();
    },
    get has_color(){ return this.__color != -1; },
    // color getter ans setter
    get color(){return this.__color;},
    set color(color){
        this.__color = color;
        board.drawBoard()
    },
    isAtBoard() {
        return this.x != -1 || this.y != -1
    },
    canDrawPen() {
        return (!this.__disable) && this.has_color && this.isAtBoard()
    },
    setPixel(){
        if(!_.isNull(progress.work)){
            Swal.fire({
                title: 'You have 2 wait',
                imageUrl:'https://aadityapurani.files.wordpress.com/2016/07/2.png',
                imageHeight:300,
                imageAlt:'wow that was rude',
                text:'Wait for your cooldown to end'
            });
        }    
        else if(_.isNull(pen.color)) {
            Swal.fire({
                icon: 'warning',
                title: 'Select Color',
                text: 'Pless select color from the table',
            });
        }
        else {
            sock.emit('set-board', {
                'color': pen.color,
                'x': pen.x,
                'y': pen.y,
            }, callback=(next_time)=>{
                if(!(_.isUndefined(next_time) || next_time == 'undefined')){
                    progress.set_time(next_time)
                }
            });
        }
    }
}



const board = {
    imgCanvas: null, imgctx:null,
    buffer: null,
    x: 0, y: 0,
    drag: { active: false, startX: 0, startY: 0, dragX: 0, dragY: 0 },
    canvas: null,
    needsdraw: false, move_vector: [0,0],
    keymove_interval:null, ctx:null,
    queue:null, buildBoard:null,
    init(){
        this.canvas = $('#board');
        this.ctx = this.canvas[0].getContext('2d');
        this.canvas.attr('alpha', 0);
        this.imgCanvas = document.createElement('canvas');
        this.imgCanvas.width = CANVAS_SIZE;
        this.imgCanvas.height = CANVAS_SIZE;
        this.imgctx = this.imgCanvas.getContext('2d');
        this.queue = [];
        this.buildBoard = _.once(this.__buildBoard)
        this.updateZoom();      // also centers
    },
    get is_ready(){return _.isNull(this.queue);},
    // level 1
    // interaction of key press
    startKeyMoveLoop(){
        board.moveBoard(
            this.move_vector[0],
            this.move_vector[1]
        )
        if(_.isNull(this.keymove_interval)){
            this.keymove_interval = setInterval(() => {
                board.moveBoard(
                    this.move_vector[0],
                    this.move_vector[1]
                );
            }, 100)
        }
    },
    // level 1
    addMovement(dir){
        dir.set = true;
        this.move_vector[0] += dir.dir[0]
        this.move_vector[1] += dir.dir[1];
        this.startKeyMoveLoop();
    },
    // level 1
    subMovement(dir){
        dir.set = false
        this.move_vector[0] -= dir.dir[0];
        this.move_vector[1] -= dir.dir[1];
        if(this.move_vector[0] == 0 && this.move_vector[1] == 0){
            clearInterval(this.keymove_interval)
            this.keymove_interval = null
        } 
    },
    //uffer on chrome takes ~1552 ms -- even less
    __buildBoard(buffer) {
        let image_data   = new ImageData(CANVAS_SIZE, CANVAS_SIZE);
        let image_buffer = new Uint32Array(image_data.data.buffer);
        buffer.forEach(function (val, index) {
            // first version of putting data, looping over the image buffer array and not of buffer of message
            //var bit = buffer[Math.floor(index/2)];
            //self.buffer[index] = reverseRGBA(COLORS[index % 2 == 0 ? bit % 16 : bit >> 4]);
            image_buffer[index * 2] = Colors.colors[val % 16].abgr;
            image_buffer[index * 2 + 1] = Colors.colors[Math.floor(val / 16)].abgr;
        });
        this.imgctx.putImageData(image_data,0,0);
        this.beforeFirstDraw();
    },
    __setAt(x, y, color){
        this.imgctx.fillStyle = color;
        this.imgctx.fillRect(x, y, 1, 1);
        this.drawBoard();
    },
    setAt(x, y, color_idx){
        // set a pixel at a position
        // x: int (0 < x < 1000)
        // y: int (0 < x < 1000)
        if(color_idx < 0 || color_idx > 15){
            // swal event
        }
        if(!(is_valid_pos(x) && is_valid_pos(y))){
            throw_message('given position of point isnt valid')
        }
        color = Colors.colors[color_idx].css_format();
        console.log(color)
        if(this.is_ready){
            this.__setAt(x, y, color)
        } else {
            this.queue.push({x:x, y:y, color:color});   // insert
        }
    },
    // empty the pixel queen
    beforeFirstDraw(){
        while(this.queue.length != 0){
            let obj = this.queue.shift();   // remove
            this.__setAt(obj.x, obj.y, obj.color);
        }
        this.queue = null;
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
    get windowBounding() { return CANVAS_SIZE * this.scale / 2; },
    // sets the board position
    // level 3
    centerPos() {
        // center axis - (window_axis_size / 2 / query.scale)
        this.x = Math.floor(query.x - board.canvas[0].width / 2 / query.scale) //( query.x - innerWidth/2)/query.scale;
        this.y = Math.floor(query.y - board.canvas[0].height / 2 / query.scale) // (query.y - innerHeight/2)/query.scale;
        pen.updateOffset()
        board.drawBoard();
    },
    // level 3
    setCanvasZoom(){
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
    setZoomStyle(){
        if(query.scale >= 25) { 
            $('#zoom-button').children('span').addClass('fa-search-minus').removeClass('fa-search-plus');
        } else {
            $('#zoom-button').children('span').addClass('fa-search-plus').removeClass('fa-search-minus');
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
            clamp(query.x + dx * this.step, CANVAS_SIZE, 0),
            clamp(query.y + dy * this.step, CANVAS_SIZE, 0)
       );
    },
    // level 1
    centerOn: function (x, y) {
        x = isNaN(x) ? query.x : clamp(x, CANVAS_SIZE, 0);
        y = isNaN(y) ? query.y : clamp(y, CANVAS_SIZE, 0);
        query.setCenter(x, y);
    },
    // level 3 in half
    updateCoords: function () {
        // not (A or B) == (not A) and (not B)
        if($('#coordinates').is(':hover')){
            $('#coordinate-slicer').text('copy')
            $('#coordinateX').text('');
            $('#coordinateY').text('');
        } else if(!board.drag.active){
            $('#coordinate-slicer').text(pen.isAtBoard() ? ',' : 'None');
            $('#coordinateX').text(pen.isAtBoard() ? pen.x : '');
            $('#coordinateY').text(pen.isAtBoard() ? pen.y : '');
        }
    },
    /* not used
    get windowrootratio(){
        return Math.sqrt(innerHeight/innerWidth);
    },
    get scalex(){
        return query.scale * this.windowrootratio;
    },
    get scaley(){
        return query.scale / this.windowrootratio
    },*/
    drawBoard(){
        if(board.needsdraw || !board.is_ready){return;}
        this.needsdraw=true;
        requestAnimationFrame(() => {  // 1-5 millisecond call, for all animation
            // it seems the average time of 5 operations is 0.23404487173814767 milliseconds
            //t = performance.now();
            this.needsdraw=false;
            this.ctx.fillStyle = BACKGROUND_COLOR
            this.ctx.fillRect(
                0,0,
                // for the scale == 0.5 scenerio
                this.canvas[0].width,
                this.canvas[0].height
            );
            this.ctx.save()
            this.ctx.imageSmoothingEnabled = false;
            this.ctx.scale(query.scale, query.scale)
            this.ctx.translate(-this.x, -this.y);
            this.ctx.drawImage(this.imgCanvas, 0, 0);
            if(pen.canDrawPen()){
                this.ctx.fillStyle = Colors.colors[pen.color].css_format(0.5);
                this.ctx.fillRect(pen.x, pen.y, 1,1);
            }
            this.ctx.restore();     // return to default position
            //performance_arr.push(performance.now()-t)
        });
    }
};
//const performance_arr = []
const sock = io();


$(document).ready(function () {
    Colors.init();
    query.init();
    board.init();
    pen.init();
    sock.on('place-start',  function(data) {
        // buffer - board in bytes
        // time - time
        progress.set_time(data.time)
        board.buildBoard(new Uint8Array(data.board));
    });    
    sock.on('set-board', (x, y, color_idx) => board.setAt(x, y, color_idx));
    sock.on('update-timer', function(time){
        progress.set_time(time);
    });
    // Lost connection
    sock.on('disconnect', () => {
        Swal.fire({
            icon: 'error',
            title: 'Lost connection with the server',
            text: 'Server Lost Connection',
          })
    });
    // Connection on
    sock.on('reconnect', () => {
        Swal.fire({
            icon: 'success',
            title: 'Reconnected to the server',
            text: 'Server Connection returned',
          })
    });
    $('#coordinates').hover(
        function(){board.updateCoords();},
        function(){board.updateCoords();}
    );
    board.canvas
    .mousemove((event) => pen.setMousePos(event))
    .mouseleave(() => pen.clearPos())
    .bind('mousewheel', (e) => {
        e.preventDefault();
        query.setScale(clamp(query.scale + Math.sign(e.originalEvent.wheelDelta)*1, MAX_SCALE, MIN_SCALE));
    })[0].addEventListener('dblclick', (event) => {   // for not breaking the 
        // jquery dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        pen.setMousePos(event);
        pen.setPixel()
    });
    board.canvas.mousedown(function (e) {
        board.drag.dragX = e.pageX;
        board.drag.dragY = e.pageY;
        board.drag.startX = query.x;
        board.drag.startY = query.y;
        board.drag.active = true;
        pen.set_cursor(MOVE_CURSOR)
    });    
    $(document).mousemove(function (e) {
        if (board.drag.active) {
            // center board
            board.centerOn(
                Math.floor(board.drag.startX + (board.drag.dragX - e.pageX) / query.scale),
                Math.floor(board.drag.startY + (board.drag.dragY - e.pageY) / query.scale)
            );
        }
    }).mouseup(() => {
        board.drag.active = false;
        pen.set_cursor(PEN_CURSOR)
    })
    $('.colorButton')
    .each(function () {
        $(this).css('background-color',
        Colors.colors[parseInt($(this).attr('value'))].css_format()); // set colors
    })
    .click(function (event) {
        event.preventDefault(); // prevent default clicking
        pen.color = parseInt($(this).attr('value'));
        $('.colorButton[state="1"]').attr('state', '0');
        $(this).attr('state', '1');
    });
    $(document).keypress(function(e) {
        // first check direction
        // https://stackoverflow.com/a/9310900
        switch (e.code) {
            case 'KeyX': {
                $('#toggle-toolbox-button').click();
                break;
            }
            case 'KeyC': {
                let button = $(".colorButton[state='1']").first();
                // if any of the is undefiend - reset
                if (_.isUndefined(button[0]) || _.isUndefined(button.next()[0])) {
                    $(".colorButton[value='0']").click();
                } else { $(button).next().click() }
                break;
            }
            case 'KeyZ': {
                let button = $(".colorButton[state='1']");
                if (_.isUndefined(button) || _.isUndefined(button.prev()[0])) {
                    $(".colorButton[value='15']").click();
                } else { $(button).prev().click() }
                break;
            }
            case 'KeyP': {
                // force keyboard if not in keyboard mode, else color a pixel
                if(pen.force_center){
                    pen.setPixel();
                } else {
                    pen.setCenterPos()
                }
            }
        }
        if(e.originalEvent.shiftKey){
            if(e.originalEvent.key == '+')      // key for plus
            {
                // option 0.5
                query.setScale(query.scale >= 1 ? query.scale + 1 : 1);
            }
            else if(e.originalEvent.key == '_'){        // key for minus
                // option 0.5
                query.setScale(query.scale > 1 ? query.scale - 1 : MIN_SCALE);
            }
        }
    }).keydown((e) => {
        keyCode = (e || window.event).keyCode;
        let dir = _.findWhere(DIRECTION_MAP, {key: keyCode})
        if ((!_.isUndefined(dir)) && !dir.set) {
            board.addMovement(dir);
        }
        
    }).keyup((e) => {
        keyCode = (e || window.event).keyCode;
        let dir = _.findWhere(DIRECTION_MAP, {key: keyCode})
        if ((!_.isUndefined(dir)) && dir.set) {
            board.subMovement(dir);
        };
        if(keyCode == ESC_KEY_CODE){ $('#logout-button').click(); }
        else if(keyCode == HOME_KEY_CODE) { $('#home-button').click(); }
    })
    // change toggle button
    $('#toggle-toolbox-button').click(function (e) {
        e.preventDefault();
        let toolbox = $('#toolbox')[0];
        // fade icons and move the toolbox down by setting its hide attribute to 1
        if(toolbox.getAttribute('hide') == 0){
            $('.icon-button').fadeOut(500)
            toolbox.setAttribute('hide', 1)
        } else {
        // reveal icons
            $('.icon-button').fadeIn(500)
            toolbox.setAttribute('hide', 0)
        }
    });
    // hash change
    $(window).bind('hashchange', function (e) {
        if (window.location.hash != query.hash) {
            query.refresh_fragments();
        }
    });
    // copy coords - https://stackoverflow.com/a/37449115
    let clipboard = new ClipboardJS(
        '#coordinates', {
            text: function() {
                return window.location.origin + window.location.pathname + query.arguments();
        }
    });
    clipboard.on('success', function(){ throw_message('Copy Success'); })
    clipboard.on('error', function(){ throw_message('Copy Error'); })
    // change zoom level
    $('#zoom-button').click(function () {
        query.setScale(
            $(this).children().hasClass('fa-search-minus')
            ? SIMPLE_UNZOOM_LEVEL
            : SIMPLE_ZOOM_LEVEL
    )});
    //logout
    $('#logout-button').click((e) => {
        // if there is any keypressed
        if(e){e.preventDefault();}
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
          if(result.value){
              window.location.href = '/logout';
          }
        });
    });
    $('#home-button').click(function(){
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
              if(result.value){
                  window.location.href = '/';
              }
          });
    });
    $(window).resize((e) => {
        board.setCanvasZoom();
    });
    //prevent resize
    /*var couponWindow = {
        width: $(window).width(),
        height: $(window).height(),
        resizing: false
      };
      var $w=$(window);
      $w.resize(function() {
        if ($w.width() != couponWindow.width && !couponWindow.resizing) {
          couponWindow.resizing = true;
          window.resizeTo(couponWindow.width, $w.height());
        }
        couponWindow.resizing = false;
      });*/
});