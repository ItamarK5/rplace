const CANVAS_SIZE = 1000;
const X_AXIS = 'x';
const Y_AXIS = 'y';
const ESC_KEY_CODE = 27;

const MIN_STEP_SIZE = 3;
const MAX_SCALE = 50;
const DRAW_COOLDOWN = 60;

const reHashX = /(?<=(^#|.+&)x=)\d+(?=&|$)/i;
const reHashY = /(?<=(^#|.+&)y=)\d+(?=&|$)/i;
const reHashScale = /(?<=(^#|.+&)scale=)\d+(?=&|$)/i;

const reArgX = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgY = /(?<=(^\x3F|.+&)x=)\d+(?=&|$)/i;
const reArgScale = /(?<=(^\x3F|.+&)scale=)\d+(?=&|$)/i;

//const reHash = /(?<=(?:^#|.+&))([\w|\d]+)=([\w|\d]+)(?=&|$)/i

const DIRECTION_MAP = [
    {key:37, dx:-1, dy:0 }, // left
    {key:39, dx: 1, dy:0 }, // right
    {key:38, dx: 0, dy:-1}, // up
    {key:40, dx: 0, dy:1 }  // down
];

const SIMPLE_ZOOM_LEVEL = 40;
const SIMPLE_UNZOOM_LEVEL = 4;
const HIDDEN_BUTTON_OPACITY = .2;
const VIEW_BUTTON_OPACITY = 1.0;


const getOffset = (x, y) => (y * CANVAS_SIZE) + x;
const getFirstIfAny = (group) => _.isNull(group) ? null : group[0]

//https://pietschsoft.com/post/2008/01/15/javascript-inttryparse-equivalent
function TryParseInt(str, defaultValue) {
    var retValue = defaultValue;
    if(!_.isNull(str)) {
        if(str.length > 0) {
            if (!isNaN(str)) {
                retValue = parseInt(str);
                console.log(retValue);
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
    get css_format() {
        return `rgba(${this.r}, ${this.g}, ${this.b}, 255)`;
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
        self.time = Date.parse(time);
        if(self.time < Date.now()){
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
        let seconds_left = Math.ceil(Math.max(this.time - Date.now(), 0) / 1000);
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
        let frags = this.fragments();
        let is_any_frag_unvalid = false;
        // x
        if((!_.isNull(frags.x)) && this.is_valid_new_x(frags.x)){
            this.x = Math.round(frags.x);            
        } else {is_any_frag_unvalid = true;}
        //y
        if((!_.isNull(frags.y)) && this.is_valid_new_y(frags.y)){
            this.y = Math.round(frags.y);            
        } else {is_any_frag_unvalid = true;}
        /// scale
        if ((!_.isNull(frags.scale)) && this.is_valid_new_scale(frags.scale)) {
            this.scale = frags.scale;
        } else {is_any_frag_unvalid = true;}
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
            scale: parseInt(getFirstIfAny(window.location.hash.match(reHashScale) || window.location.search.match(reArgScale)))
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

var board = {
    image: null,
    buffer: null,
    x: 0, y: 0,
    scale: SIMPLE_UNZOOM_LEVEL,
    drag: { active: false, startX: 0, startY: 0, dragX: 0, dragY: 0 },
    color: null, rel_pos: { x: 0, y: 0 },
    zoomer: null, canvas:       null,
    mover:  null, container:    null,
    init: function () {
        this.zoomer = $('#board-zoomer');
        this.container = $('#board-container');
        this.canvas = $('#board');
        this.mover = $('#board-mover');
        this.canvas.attr('alpha', 0);
        this.updateZoom();      // also centers
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
        self.drawBoard();
    },

    drawBoard: function () {
        $('#board')[0].getContext('2d').putImageData(this.image, 0, 0);
        let self = this;
        window.requestAnimationFrame(function () { self.drawBoard(); });
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

    getCoords: function (e) {
        return {
            x: Math.floor((e.pageX - this.mover[0].getClientRects()[0].left) / board.scale),
            y: Math.floor((e.pageY - this.mover[0].getClientRects()[0].top) / board.scale)-1 // because reasons, during debugging it come to this;
        };
    },
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
    updateZoom: function () {
        this.scale = query.scale;
        this.zoomer.css('transform', `scale(${this.scale}, ${this.scale})`);
        let zoom_state = this.scale >= 25 ? 'zoom-out' : 'zoom-in';
        if (zoom_state != $('#zoom').attr('state')) {
            $('#zoom').attr('state', zoom_state);
        }
        this.centerPos();
    },
    get step() {
        // the scale is inproportion to the step size
        return MIN_STEP_SIZE * MAX_SCALE / this.scale;
    },
    keep_inside_border: function (pos) {
        //return change;
        return Math.max(0, Math.min(pos, CANVAS_SIZE));
    },
    moveBoard: function (dir) {
        /*      let x = this.keep_inside_border(this.real_x, dir[DIR_INDEX_XNORMAL]*this.step*this.scale, rect.left, rect.right)/this.scale;
              let y = this.keep_inside_border(this.real_y, dir[DIR_INDEX_YNORMAL]*this.step*this.scale, rect.top, rect.bottom)/this.scale;
              console.log(x, y);
        */
       let x = this.keep_inside_border(query.x + dir.dx * this.step);
       let y = this.keep_inside_border(query.y + dir.dy * this.step);
       query.set_center(x, y);
    },
    centerOn: function (x, y) {
        x = isNaN(x) ? query.x : this.keep_inside_border(x);
        y = isNaN(y) ? query.y : this.keep_inside_border(y);
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
            $('#coordX').text(board.x_mouse != -1 ? this.x_mouse + 1 : 'none');
            $('#coordY').text(board.y_mouse != -1 ? this.y_mouse + 1 : 'none');
        }
    },
    // using clipboard.js
    // https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/write
};
$(document).ready(function () {
    Colors.init();
    query.init();
    board.init();
    var sock = io();
    sock.on('place-start',  function(data) {
        // buffer - board in bytes
        // time - time
        board.buildBoard(new Uint8Array(data.board));
        progress.set_time(data.time)
    });
    
    sock.on('set-board', function (params) {
        let color_idx = parseInt(params['color']);
        let x = parseInt(params['x']);
        let y = parseInt(params['y']);
        board.buffer[getOffset(x, y)] = Colors.colors[color_idx].abgr;
    });
    
    sock.on('update-timer', function(time){
        progress.set_time(time);
    });
    $('#coords').hover(
        function(){board.update_coords();},
        function(){board.update_coords();}
    );
    board.canvas.mousemove(function (e) {
        let coords = board.getCoords(event);
        if (coords.x >= 0 && 1000 > coords.x && coords.y >= 0 && 1000 > coords.y) {
            board.x_mouse = coords.x;
            board.y_mouse = coords.y;
        } else { board.x_mouse = board.y_mouse = -1;} //set the strings null 
        board.update_coords();
    }).mouseleave(function () {
        board.x_mouse = board.y_mouse = -1; 
        board.update_coords();
    })[0].addEventListener('dblclick', function () {   // for not breaking the 
        // jquery dblclick dont work on some machines but addEventListner does 
        // source: https://github.com/Leaflet/Leaflet/issues/4127
        /*Get XY https://codepo8.github.io/canvas-images-and-pixels/#display-colour*/
        if(!_.isNull(progress.work)){
            Swal.fire({
                icon: 'warning',
                title: 'You have 2 wait',
                text: 'You need to end for your time to finish',
              });
        }    
        else if(_.isNull(board.color)) {
            Swal.fire({
                icon: 'warning',
                title: 'Select Color',
                text: 'Pless select color from the table',
              })
        }
        else {
            sock.emit('set-board', {
                'color': board.color,
                'x': board.x_mouse,
                'y': board.y_mouse,
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
    }).mouseup(function (e) {
        board.drag.active = false;
    });
    
    $('.colorBtn').each(function () {
        $(this).css('background-color', Colors.colors[parseInt($(this).attr('value'))].css_format); // set colors
    }).click(function (event) {
        event.preventDefault(); // prevent default clicking
        board.color = parseInt($(this).attr('value'));
        $('.colorBtn[state="1"]').attr('state', '0');
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
                let button = $(".colorBtn[state='1']").first();
                // if any of the is undefiend - reset
                if (_.isUndefined(button[0]) || _.isUndefined(button.next()[0])) {
                    $(".colorBtn[value='0']").click();
                } else { $(button).next().click() }
                break;
            }
            case 'KeyZ': {
                let button = $(".colorBtn[state='1']");
                if (_.isUndefined(button) || _.isUndefined(button.prev()[0])) {
                    $(".colorBtn[value='15']").click();
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
    }).keydown(function(e){
        keyCode = (e || window.event).keyCode;
        let dir = _.findWhere(DIRECTION_MAP, {key: keyCode})
        if (!_.isUndefined(dir)) {
            board.moveBoard(dir);
        } 
        if(keyCode == ESC_KEY_CODE){ quit_painter_alert(); }
    });
    // change zoom level
    $('#zoom').click(function () {query.set_scale(
            this.getAttribute('state') == 'zoom-out' 
            ? SIMPLE_UNZOOM_LEVEL
            : SIMPLE_ZOOM_LEVEL
    )});
    // change toggle button
    $('#toggle-toolbox-button').click(function (e) {
        e.preventDefault();
        let toolbox = $('#toolbox')[0];
        toolbox.setAttribute('hide', 1 - (1 * TryParseInt(toolbox.getAttribute('hide'), 0)))
    });
    // hash change
    $(window).bind('hashchange', function (e) {
        if (window.location.hash != query.hash) {
            query.refresh_fragments();
        }
    });
    $('#logout-button').click(quit_painter_alert);
    // copy coords - https://stackoverflow.com/a/37449115
    let clipboard = new ClipboardJS(
        '#coords', {
        text: function() {
            return window.location.origin + window.location.pathname + query.arguments();
        }
    });
    clipboard.on('success', function(){ throw_message('Copy Success'); })
    clipboard.on('error', function(){ throw_message('Copy Error'); })
});