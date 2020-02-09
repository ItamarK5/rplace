const CANVAS_SIZE = 1000;
const X_AXIS = 'x';
const Y_AXIS = 'y';
const ESC_KEY_CODE = 27;
const TIMEZONE_FACTOR = 60*1000;    // 60000
const MIN_STEP_SIZE = 3;
const MAX_SCALE = 50;
const DRAW_COOLDOWN = 60;

const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;
const reHashScale = /(?<=(^#|.+&)scale=)\d{1,2}(\x2E\d+)?(?=&|$)/i;

const reArgX = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgY = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgScale = /(?<=(^\x3F|.+&)scale=)\d{1,2}(\x2E\d+)?(?=&|$)/i;

// indexes for set-board package
const SET_BOARD_PARAM_Y_IDX = 0;
const SET_BOARD_PARAM_X_IDX = 1
const SET_BOARD_PARAMS_COLOR_IDX = 2;

//const reHash = /(?<=(?:^#|.+&))([\w|\d]+)=([\w|\d]+)(?=&|$)/i


const DIRECTION_MAP = [
    {key:37, dir:[-1,  0], set:false}, // left
    {key:39, dir:[ 1,  0], set:false}, // right
    {key:38, dir:[ 0, -1], set:false}, // up
    {key:40, dir:[ 0,  1], set:false}  // :own
];

const SIMPLE_ZOOM_LEVEL = 40;
const SIMPLE_UNZOOM_LEVEL = 4;
const HIDDEN_BUTTON_OPACITY = .2;
const VIEW_BUTTON_OPACITY = 1.0;


const getOffset = (x, y) => (y * CANVAS_SIZE) + x;
const getFirstIfAny = (group) => _.isNull(group) ? null : group[0]
const clamp = (v, max, min) => Math.max(min, Math.min(v, max));
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

function quit_painter_alert() {
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
};

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
    css_format(alpha=255) {
        return `rgba(${this.r}, ${this.g}, ${this.b}, ${alpha})`;
    }
}


var Colors = {
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

var progress = {
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
            self.work = setInterval(function () { self.update_timer() }, 50);
       }
    },
    update_timer() {
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


var query = {
    x: 500,        // the x of the center pixel in the canvas on screen
    y: 500,        // the y of the center pixel in the canvas on screen
    scale: 4,
    // initialize the 
    init: function () {
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
    hash : function() {
        return `#${this.__path}`
    },
    arguments : function() {
        return `?${this.__path}`
    },
    // validation check fo reach attributes
    is_valid_new_x: (val) => 0 <= val && val < CANVAS_SIZE && val != this.x,
    is_valid_new_y: (val) => 0 <= val && val < CANVAS_SIZE && val != this.y,
    is_valid_new_scale: (val) => 0.5 <= val && val <= MAX_SCALE && val != this.scale,
    // use regex to get fragments
    fragments: function() {
        return {
            // first checks the hash if there are none, check the location
            x: parseInt(getFirstIfAny(window.location.hash.match(reHashX) || window.location.search.match(reArgX))),
            y: parseInt(getFirstIfAny(window.location.hash.match(reHashY) || window.location.search.match(reArgY))),
            scale: parseFloat(getFirstIfAny(window.location.hash.match(reHashScale) || window.location.search.match(reArgScale)))
        };
    },
    // set x and
    set_center: function (x = undefined, y = undefined, to_update = true) {
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
    set_scale: function(scale, to_update = true) {
        if(this.is_valid_new_scale(scale)){
            this.scale = scale;
            if(this.scale < 1)
            {
                this.set_center(CANVAS_SIZE/2, CANVAS_SIZE/2, false);
            }
            if(to_update){
                board.updateZoom();
            }
            this.set_window_hash()
        }
    },
    refresh_fragments: function (to_update) {
        /*  refresh_fragments(bool) -> void
         *  refresh the query object by the current hash values if they are valid
         */
        let frags = this.fragments();
        if ((!isNaN(frags.x)) || (!isNaN(frags.y))) {
            this.set_center(parseInt(frags.x), parseInt(frags.y), to_update);
        }
        /// update scale
        if (isNaN(frags.scale) && this.is_valid_new_scale(parseInt(frags.scale))) {
            this.scale = this.scale;
            if (to_update) {
                query.updateZoom()
            }
        }
    },
    // set the window.loaction.hash to the query hash value
    set_window_hash: function() {
        //  update location
        if (window.location.hash != this.hash) {
            // change hash without triggering events
            history.replaceState(null, null, document.location.pathname  + this.hash());
            //window.location.hash = this.hash;
        }
    }
}


const pen = {
    x:null,
    y:null,
    reminderX:null,
    reminderY:null,
    __color:0,
    canvas:null,
    needsdraw:false,
    init() {
        this.color = $('.colorButton').index('[state="1"]')
        this.canvas = $('#pen');
        let ctx = this.canvas[0].getContext('2d');
        ctx.globalAlpha = 0.9;
        ctx.fillStyle = 'rgba(0,0,0,0)'
        ctx.fillRect(0,0,1000,1000);
    },
    update_offset(canvas_event) {
        /*this.x = canvas_event.offsetX;
        this.y = canvas_event.offsetY;*/
        let x = Math.floor((canvas_event.pageX - board.mover[0].getClientRects()[0].left) / board.scale);
        let y = Math.floor((canvas_event.pageY - board.mover[0].getClientRects()[0].top) / board.scale)-1 // because reasons, during debugging it come to this;
        if (!(x >= 0 && 1000 > x && y >= 0 && 1000 > y)) {
           this.clear_pos(); // set values to -1
        } else if(x != this.x || y != this.y){
            this.x = x;
            this.y = y;
            this.updatePen()
        }
    },
    
    set_pos(canvas_event){
        this.update_offset(canvas_event);
        board.update_coords();   
        this.updatePen()  
    },
    clear_pos(){
        this.x = this.y = -1;
        board.update_coords();
    },
    get has_color(){ return this.__color != -1; },
    // color getter ans setter
    get color(){return this.__color;},
    set color(color){
        this.__color = color;
        board.updateBoard()
    },
    is_at_board() {
        return this.x != -1 && this.y != -1
    },
    has_old_xy() {
        return !(_.isNull(this.oldX) || _.isNull(this.oldY))
    },
    canUpdatePen() {
        return (!this.needsdraw) && this.has_color && this.is_at_board() && this.has_old_xy()
    },
    updatePen(){
        if(!this.canUpdatePen()){
            return;
        }
        this.needsdraw = true;
        let self =this;
        window.requestAnimationFrame(() => {
            let ctx = self.canvas[0].getContext('2d');
            // must check
            if(!(_.isNull(pen.reminderX) || _.isNull(pen.reminderY))){
                ctx.clearRect(pen.reminderX, pen.reminderY, 1, 1);
            }
            pen.reminderX = pen.x;
            pen.reminderY = pen.y;
            if(self.has_color){
                ctx.fillStyle = ctx.fillStyle = Colors.colors[self.color].css_format(0.5)
                ctx.fillRect(pen.x,pen.y,1,1);
                self.needsdraw =false;
            }
        })
    }
}



var board = {
    image: null,
    buffer: null,
    x: 0, y: 0,
    scale: SIMPLE_UNZOOM_LEVEL,
    drag: { active: false, startX: 0, startY: 0, dragX: 0, dragY: 0 },
    color: null, rel_pos: { x: 0, y: 0 },
    zoomer: null, canvas:       null,
    mover:  null, container:    null,
    needsdraw: false, move_vector: [0,0],
    keymove_interval:null,
    ready:false,
    init: function () {
        this.zoomer = $('#board-zoomer');
        this.container = $('#board-container');
        this.canvas = $('#board');
        this.mover = $('#board-mover');
        this.canvas.attr('alpha', 0);
        this.updateZoom();      // also centers
        this.startKeyMoveLoop()
    },
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
                )
            }, 100);
        }
    },
    addMovement(dir){
        dir.set = true;
        this.move_vector[0] += dir.dir[0]
        this.move_vector[1] += dir.dir[1]
        this.startKeyMoveLoop()
    },
    subMovement(dir){
        dir.set = false;
        this.move_vector[0] -= dir.dir[0]
        this.move_vector[1] -= dir.dir[1]
        if(this.move_vector[0] == 0 && this.move_vector[1] == 0){
            clearInterval(this.keymove_interval);
            this.keymove_interval = null;
        }
    },
    // on chrome takes ~1552 ms -- even less
    buildBoard: function (buffer) {
        this.image = new ImageData(CANVAS_SIZE, CANVAS_SIZE);
        this.buffer = new Uint32Array(this.image.data.buffer);
        let self = this;
        //var t = Date.now(); deubg time
        buffer.forEach(function (val, index) {
            // first version of putting data, looping over the image buffer array and not of buffer of message
            //var bit = buffer[Math.floor(index/2)];
            //self.buffer[index] = reverseRGBA(COLORS[index % 2 == 0 ? bit % 16 : bit >> 4]);
            self.buffer[index * 2] = Colors.colors[val % 16].abgr;
            self.buffer[index * 2 + 1] = Colors.colors[Math.floor(val / 16)].abgr;
        });
        // copying r/place, using Uint32Array to store the values
        //console.log(Date.now()-t); deubg time
        this.ready = true;
        self.updateBoard();
    },

    updateBoard: function () {
        /* https://josephg.com/blog/rplace-in-a-weekend/*/
        if(this.needsdraw || !this.ready){return;}
        let self = this;
        requestAnimationFrame(function() {  // 1 millisecond call, for all animation
            ctx = self.canvas[0].getContext('2d');
            /*ctx.fillStyle = '#eee'
            ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
            ctx.save();
            ctx.imageSmoothingEnabled = false;
            ctx.scale(query.scale, query.scale);
            ctx.translate(-board.x, -board.y);
            ctx.restore();*/
            ctx.putImageData(self.image, 0, 0);
        })
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
    centerPos: function () {
        this.x = CANVAS_SIZE/2 - query.x;
        this.y = CANVAS_SIZE/2 - query.y;
        this.mover.css('transform', "translate("
            + (this.scale <= 1 ? Math.round(this.x) : this.x) + "px, "
            + (this.scale <= 1 ? Math.round(this.y) : this.y) + "px)"
        );
    },
    updateZoom() {
        this.scale = query.scale;
        this.zoomer.css('transform', `scale(${this.scale}, ${this.scale})`);
        this.setZoomStyle()
        this.centerPos();
    },
    setZoomStyle(){
        if(this.scale >= 25) { 
            $('#zoom-button').children('span').addClass('fa-search-minus').removeClass('fa-search-plus');
        } else {
            $('#zoom-button').children('span').addClass('fa-search-plus').removeClass('fa-search-minus');
        }
    },
    get step() {
        // the scale is inproportion to the step size
        return MIN_STEP_SIZE * MAX_SCALE / this.scale;
    },

    moveBoard: function (dx, dy) {
        /*      let x = this.keep_inside_border(this.real_x, dir[DIR_INDEX_XNORMAL]*this.step*this.scale, rect.left, rect.right)/this.scale;
              let y = this.keep_inside_border(this.real_y, dir[DIR_INDEX_YNORMAL]*this.step*this.scale, rect.top, rect.bottom)/this.scale;
              console.log(x, y);
        */
       query.set_center(
        clamp(query.x + dx/10 * this.step, CANVAS_SIZE, 0),
        clamp(query.y + dy/10 * this.step, CANVAS_SIZE, 0)
       );
    },
    centerOn: function (x, y) {
        x = isNaN(x) ? query.x : clamp(x, CANVAS_SIZE, 0);
        y = isNaN(y) ? query.y : clamp(y, CANVAS_SIZE, 0);
        query.set_center(x, y);
    },
    update_coords: function () {
        // not (A or B) == (not A) and (not B)
        if($('#coords').is(':hover')){
            $('#coord-slicer').text('copy')
            $('#coordX').text('');
            $('#coordY').text('');
        } else if(!board.drag.active){
            $('#coord-slicer').text(',');
            $('#coordX').text(pen.x != -1 ? pen.x : 'none');
            $('#coordY').text(pen.y != -1 ? pen.y : 'none');
        }
    },
    // using clipboard.js
    // https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/write
};
$(document).ready(function () {
    Colors.init();
    query.init();
    board.init();
    pen.init();
    var sock = io();
    sock.on('place-start',  function(data) {
        // buffer - board in bytes
        // time - time
        board.buildBoard(new Uint8Array(data.board));
        progress.set_time(data.time)
    });    
    sock.on('set-board', function (x, y, color_idx) {
        //let x = params[SET_BOARD_PARAM_X_IDX];
        //let y = params[SET_BOARD_PARAM_Y_IDX];
        //let color_idx = params[SET_BOARD_PARAMS_COLOR_IDX];
        console.log(x,y, color_idx);
        board.buffer[getOffset(x, y)] = Colors.colors[color_idx].abgr;
        board.updateBoard()
    });
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
    $('#coords').hover(
        function(){board.update_coords();},
        function(){board.update_coords();}
    );
    board.canvas
    .mousemove((event) => pen.set_pos(event))
    .mouseleave(() => pen.clear_pos())
    .bind('mousewheel', (event) => {
        query.set_scale(Math.max(query.scale + Math.sign(event.originalEvent.wheelDelta), 0.9));
    })[0].addEventListener('dblclick', (event) => {   // for not breaking the 
        // jquery dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        pen.set_pos(event);
        if(!_.isNull(progress.work)){
            Swal.fire({
                icon: 'warning',
                title: 'You have 2 wait',
                text: 'You need to end for your time to finish',
              });
        }    
        else if(_.isNull(pen.color)) {
            Swal.fire({
                icon: 'warning',
                title: 'Select Color',
                text: 'Pless select color from the table',
              })
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
            })
        }
    });
    board.zoomer.mousedown(function (e) {
        board.drag.dragX = e.pageX;
        board.drag.dragY = e.pageY;
        board.drag.startX = query.x;
        board.drag.startY = query.y;
        board.drag.active = true;
    });    
    $(document).mousemove(function (e) {
        if (board.drag.active) {
            // center board
            board.centerOn(
                Math.round(board.drag.startX + (board.drag.dragX - e.pageX) / board.scale),
                Math.round(board.drag.startY + (board.drag.dragY - e.pageY) / board.scale)
            );
        }
    }).mouseup(() => {
        board.drag.active = false;
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
        }
        if(e.originalEvent.shiftKey){
            if(e.originalEvent.key == '+')      // Plues
            {
                query.set_scale(query.scale >= 1 ? query.scale + 1 : 1);
            }
            else if(e.originalEvent.key == '_'){        // key for minus
                query.set_scale(query.scale > 1 ? query.scale - 1 : 0.5);
            }
        }
    }).keydown((e) => {
        keyCode = (e || window.event).keyCode;
        let dir = _.findWhere(DIRECTION_MAP, {key: keyCode})
        if ((!_.isUndefined(dir)) && !dir.set) {
            board.addMovement(dir)
        }
        if(keyCode == ESC_KEY_CODE){ quit_painter_alert(); }
    }).keyup((e) => {
        keyCode = (e || window.event).keyCode;
        let dir = _.findWhere(DIRECTION_MAP, {key: keyCode})
        if ((!_.isUndefined(dir)) && dir.set) {
            board.subMovement(dir);
        };
    })
    // change toggle button
    $('#toggle-toolbox-button').click(function (e) {
        e.preventDefault();
        let toolbox = $('#toolbox')[0];
        if(toolbox.getAttribute('hide') == 0){
            $('.icon-button').fadeOut(500)
            toolbox.setAttribute('hide', 1)
        } else {
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
        '#coords', {
        text: function() {
            return window.location.origin + window.location.pathname + query.arguments();
        }
    });
    clipboard.on('success', function(){ throw_message('Copy Success'); })
    clipboard.on('error', function(){ throw_message('Copy Error'); })
    // change zoom level
    $('#zoom-button').click(function () {
        query.set_scale(
            $(this).children().hasClass('fa-search-minus')
            ? SIMPLE_UNZOOM_LEVEL
            : SIMPLE_ZOOM_LEVEL
    )});
    //logout
    $('#logout-button').click(quit_painter_alert);
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
});