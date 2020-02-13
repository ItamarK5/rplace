const CANVAS_SIZE = 1000;
const ESC_KEY_CODE = 27;
const HOME_KEY_CODE = 36;
const MIN_STEP_SIZE = 3;
const MIN_SCALE = 0.5;
const MAX_SCALE = 50;
const DRAW_COOLDOWN = 60;

const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;
const reHashScale = /(?<=(^#|.+&)scale=)\d{1,2}(\x2E\d+)?(?=&|$)/i;

const reArgX = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgY = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgScale = /(?<=(^\x3F|.+&)scale=)\d{1,2}(\x2E\d+)?(?=&|$)/i;

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
const is_valid_scale = (scale) => MIN_SCALE <= scale && scale <= MAX_SCALE;
const is_valid_pos = (v) => 0 <= v < CANVAS_SIZE;
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
    hash() {
        return `#${this.__path}`
    },
    arguments() {
        return `?${this.__path}`
    },
    // validation check fo reach attributes
    is_valid_new_x(val) {return !isNaN(val) && is_valid_pos(val) && val != this.x },
    is_valid_new_y(val) {return !isNaN(val) && is_valid_pos(val) && val != this.y },
    is_valid_new_scale(val) {return !isNaN(val) && is_valid_scale(val) && val != this.scale },
    // use regex to get fragments
    fragments() {
        return {
            // first checks the hash if there are none, check the location
            x: parseInt(getFirstIfAny(window.location.hash.match(reHashX) || window.location.search.match(reArgX))),
            y: parseInt(getFirstIfAny(window.location.hash.match(reHashY) || window.location.search.match(reArgY))),
            scale: parseFloat(getFirstIfAny(window.location.hash.match(reHashScale) || window.location.search.match(reArgScale)))
        };
    },
    // set x and
    set_center(x = undefined, y = undefined, to_update = true) {
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
    set_scale(scale, to_update = true) {
        if(this.is_valid_new_scale(scale)){
            this.scale = scale;
            if(this.scale < Math.min(innerWidth/board.width, innerHeight/board.height))
            {
                this.set_center(CANVAS_SIZE/2, CANVAS_SIZE/2, false);
            }
            if(to_update){
                board.updateZoom();
            }
            this.set_window_hash()
        }
    },
    refresh_fragments(to_update) {
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
    set_window_hash() {
        //  update location
        if (window.location.hash != this.hash) {
            // change hash without triggering events
            history.replaceState(null, null, document.location.pathname  + this.hash());
            //window.location.hash = this.hash;
        }
    }
}


const pen = {
    x:null, y:null, canvas:null,
    init() {
        this.color = $('.colorButton').index('[state="1"]')
    },
    mousePos(e){
        let x = Math.floor((e.pageX - $(board.canvas).offset().left) / board.scale);
        let y = Math.floor((e.pageY - $(board.canvas).offset().top) / board.scale)-1; // because reasons, during debugging it come to this;
        return {x:x, y:y}
    },
    updateOffset(pos) {
        /*this.x = canvas_event.offsetX;
        this.y = canvas_event.offsetY;*/
        // read this https://stackoverflow.com/a/12142675
        if (!(pos.x >= 0 && 1000 > pos.x && pos.y >= 0 && 1000 > pos.y)) {
           this.clearPos(); // set values to -1
        } else if(pos.x != this.x || pos.y != this.y){
            this.x = pos.x;
            this.y = pos.y;
            board.updateScreen()
        }
    }, 
    setMousePos(canvas_event){
        this.updatePos(this.mousePos(canvas_event));
    },
    setSimplePos(){
        this.updatePos({x:query.x, y:query.y});
    },
    updatePos(pos){
        this.updateOffset(pos)
        board.updateCoords();   
        board.updateScreen();
    },
    clearPos(){
        this.x = this.y = -1;
        board.updateCoords();
    },
    get has_color(){ return this.__color != -1; },
    // color getter ans setter
    get color(){return this.__color;},
    set color(color){
        console.log(color);
        this.__color = color;
        board.updateScreen()
    },
    is_at_board() {
        return this.x != -1 && this.y != -1
    },
    canUpdatePen() {
        return this.has_color && this.is_at_board()
    },
}



const board = {
    image: null,
    buffer: null,
    x: 0, y: 0,
    scale: SIMPLE_UNZOOM_LEVEL,
    drag: { active: false, startX: 0, startY: 0, dragX: 0, dragY: 0 },
    zoomer: null, canvas:       null,
    mover:  null, container:    null,
    needsdraw: false, move_vector: [0,0],
    keymove_interval:null, ctx:null,
    queue:null,
    init(){
        this.zoomer = $('#board-zoomer');
        this.container = $('#board-container');
        this.canvas = $('#board');
        this.ctx = this.canvas[0].getContext('2d');
        this.mover = $('#board-mover');
        this.canvas.attr('alpha', 0);
        this.queue = [];
        this.updateZoom();      // also centers
    },
    get is_ready(){return _.isNull(this.queue);},
    startKeyMoveLoop(){
        board.moveBoard(
            this.move_vector[0],
            this.move_vector[1]
        )       
        this.keymove_interval = setInterval(() => {
            board.moveBoard(
                this.move_vector[0],
                this.move_vector[1]
            );
            pen.setSimplePos();
        }, 100);
    },
    addMovement(dir){
        dir.set = true;
        this.move_vector[0] += dir.dir[0]
        this.move_vector[1] += dir.dir[1]
        this.startKeyMoveLoop();
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
    buildBoard(buffer) {
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
        this.queue = null;
        this.updateScreen()
    },
    setAt(x, y, color_idx){
        color = Colors.colors[color_idx].abgr;
        if(this.is_ready){
            board.buffer[getOffset(x, y)] = color;
            this.updateZoom()
        } else {
            console.log(this.is_ready)
            this.queue.push({x:x, y:y, color:color});
        }
    },
    // empty the pixel queen
    emptyBoardQueue(){async () => {
        color = Colors.colors[color_idx].abgr;
        while(!_.isNull(queue)){
            setPlace = this.queue.shift()
            board.buffer[getOffset(setPlace.x, setPlace.y)] = setPlace.color;
        }
        this.queue = null;
        this.updateScreen();
    }
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
    centerPos() {
        this.x = CANVAS_SIZE/2 - query.x;
        this.y = CANVAS_SIZE/2 - query.y;
        this.mover.css('transform', "translate("
            + (this.scale <= 1 ? Math.round(this.x) : this.x) + "px, "
            + (this.scale <= 1 ? Math.round(this.y) : this.y) + "px)"
        );
        console.log(this.x, this.y);
        board.updateScreen();
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
    moveBoard(dx, dy) {
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
    updateCoords: function () {
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
    updateScreen(){
        if(board.needsdraw || !board.is_ready){return;}
        this.needsdraw=true;
        requestAnimationFrame(() => {  // 1-4 millisecond call, for all animation
            /*ctx.fillStyle = '#eee'
            ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);
            ctx.save();
            ctx.imageSmoothingEnabled = false;
            ctx.scale(query.scale, query.scale);
            ctx.translate(-board.x, -board.y);
            ctx.restore();*/
            this.ctx.fillStyle = 'gray'
            this.ctx.fillRect(1000, 1000, 0, 0)
            this.needsdraw=false;
            this.ctx.putImageData(this.image, 0, 0);
            if(pen.canUpdatePen()){
                this.ctx.fillStyle = Colors.colors[pen.color].css_format(0.5)
                this.ctx.fillRect(pen.x,pen.y,1,1);
            }
        });
    }
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
    $('#coords').hover(
        function(){board.updateCoords();},
        function(){board.updateCoords();}
    );
    board.canvas
    .mousemove((event) => pen.setMousePos(event))
    .mouseleave(() => pen.clearPos())
    .bind('mousewheel', (e) => {
        e.preventDefault();
        query.set_scale(clamp(query.scale + Math.sign(e.originalEvent.wheelDelta)*0.5, MAX_SCALE, MIN_SCALE));
    })[0].addEventListener('dblclick', (event) => {   // for not breaking the 
        // jquery dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        pen.setMousePos(event);
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
                Math.floor(board.drag.startX + (board.drag.dragX - e.pageX) / board.scale),
                Math.floor(board.drag.startY + (board.drag.dragY - e.pageY) / board.scale)
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
                query.set_scale(query.scale >= 1 ? query.scale + 0.5 : 1);
            }
            else if(e.originalEvent.key == '_'){        // key for minus
                query.set_scale(query.scale > 1 ? query.scale - 0.5 : MIN_SCALE);
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
    //prevent resize
    $(window).resize(function(){
        window.resizeTo(size[0],size[1]);
    });
});