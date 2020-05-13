/**
 * @summary Type defections
 * @typedef {Vector2D|number[]|Object.{x:number, y:number:number}} Vector2DType type for function that require 2d vector object @see {@link:Vector2D}
 */

/** 
 * @param {*} caller of the function
 * @param {function} call function to that gets 1 arguments and returns nothing
 * @param {*} val value passed as parameter
 * executes the function only  
*/
const __vector2ArgsOperationWrapper = (caller, call, val) => {
	if(!_.isUndefined(val)){
		call.apply(caller, [val]);
	}
}

/**
 * @class Vector2D
 * @classdesc class representing a 2d vector
 * a class with simple operations between vectors
 * the class suppose massive operations, using 1 code line chained function to return 1 object.
 */
class Vector2D {
	/**
	 * @returns {Vector2D} returns zero vector, Vector(0,0)
	 * the zero of vector
	 */
	static zero(){
		return new Vector2D(0, 0);
	}
	/**
	 * @param {Vector2DType} v a vector object
	 * @returns {Vector2D} 2d vector type
	 * evaluates the object as 2D vector
	 */
	static evalVector(v){
		if(v instanceof Vector2D){
			return v;
		// if array
		} else if(v instanceof Array && v.length == 2){
			return new Vector2D(v[0], v[1]);
		// if object
		} else if(v instanceof Object && _.keys(v) == ["x", "y"]){
			return new Vector2D(v.x, v.y)
		}
		// else
		return undefined;
	}
	/**
	 * @param {number} x - x value
	 * @param {numBer} y - y value
	 */
	constructor(x, y){
		this.__x = x;
		this.__y = y;
	}
	/**
	 * gets the x value of the instance
	 * @returns {number} x
	 */
	get x(){
		return this.__x;
	}
	/**
	 * gets the y value of the instance
	 * @returns {number} y
	 */
	get y(){
		return this.__y;
	}
	/**
	 * @param {*} val a value
	 * @returns {NaN|Number} NaN if val isnt a number otherwise returns
	 * utility function to check if value is number of not, if the value is SET to NaN all values become NaN
	 */
	static _evalSafe(val){
		return _.isNumber(val) ? val : NaN
	}
	/**
	 * 
	 * @param {*} x value
	 * @returns {Vector2D} itself for mass operation
	 * set current x, if x param isn't a number its sets to NaN
	 */
	setX(x){
		this.__x = Vector2D._evalSafe(x)
		return this;
	}
	/**
	 * 
	 * @param {*} y value
	 * @returns {Vector2D} itself for mass operation
	 * set current y, if y param isn't a number its sets to NaN
	 */
	setY(y){
		this.__y = Vector2D._evalSafe(y)
		return this;
	}
	/**
	 * x and y can be anything but we hope they are numbers
	 * @param {*} x x value
	 * @param {*} y y value
	 * @returns {Vector2D} itself for mass operation
	 * sets x and y but also
	 */
	setXY(x, y){
		__vector2ArgsOperationWrapper(this, this.setX, x);
		__vector2ArgsOperationWrapper(this, this.setY, y);
		return this;
	}
	/**
	 * 
	 * @param {*} x a value, hoping a number
	 * @returns {Vector2D} itself for mass operation
	 * sets the x if the value is valid (a number => not NaN) otherwise dont set
	 */
	setXIfValid(x){
		let safe_x = Vector2D._evalSafe(x);
		if(!isNaN(safe_x)){
			this.__x = safe_x
		}
		return this;
	}
	/**
	 * 
	 * @param {*} y a value, hoping a number
	 * @returns {Vector2D} itself for mass operation
	 * sets the x if the value is valid (a number => not NaN) otherwise dont set
	 */
	setYIfValid(y){
		let safe_y = Vector2D._evalSafe(y);
		if(!isNaN(safe_y)){
			this.__y = safe_y
		}
		return this;
	}
	/**
	 * 
	 * @param {*} x x value to set
	 * @param {*} y y value to set
	 * sets the x and y if x and y are valid numbers
	 * can use the simple functions because it doesn't set them if undefined
	 */
	setXYIfValid(x, y){
		this.setXIfValid(x);
		this.setYIfValid(y);
		return this;
	}
	/**
	 * 
	 * @param {*} x object, hoping to be a number
	 * adds the value to the x property (if isn't a number sets to NaN)
	 */
	addX(x){ 
		this.__x += Vector2D._evalSafe(x); 
		return this; 
	}
	/**
	 * 
	 * @param {*} y object, hoping to be a number
	 * adds the value to the x property (if isn't a number sets to NaN)
	 */
	addY(y){ 
		this.__y +=  Vector2D._evalSafe(y);
		return this; 
	}
	/**
	 * 
	 * @param {*} x object, hoping to be a number
	 * @param {*} y object, hoping to be a number
	 * adds the value to the x, y properties (if they aren't each number sets to NaN)
	 * also if they undefined don't try to set
	 */
	addXY(x, y) {
		__vector2ArgsOperationWrapper(this, this.addX, x);
		__vector2ArgsOperationWrapper(this, this.addY, y);
		return this;
	}
	/**
	 * 
	 * @param {Vector2DType} other another vector object
	 * adds the object in unsafe mode, if the other object cant be evaled as vector, x and y become NaN
	 */
	addVector(other) {
		let other_vector = Vector2D.evalVector(other);
		if(!other_vector){
			this.x = NaN;
			this.y = NaN;
		}
		this.addXY(other_vector.x, other_vector.y);
		return this;
	}
	/**
	 * 
	 * @param {*} x a value, hoping a number
	 * @returns {Vector2D} itself for mass operation
	 * adds the x if the value is valid (a number => not NaN) otherwise don't add
	 */
	addXIfValid(x){ 
		this.setXIfValid(Vector2D._evalSafe(x) + this.__x);
		return this; 
	}
	/**
	 * 
	 * @param {*} y a value, hoping a number
	 * @returns {Vector2D} itself for mass operation
	 * adds the y if the value is valid (a number => not NaN) otherwise don't add
	 */
	addYIfValid(y){ 
		this.setYIfValid(Vector2D._evalSafe(y) + this.__y);
		return this; 
	}
	/**
	 * 
	 * @param {*} x added x value 
	 * @param {*} y added y value
	 * added the values of x and y if there are valid, because the called methods dont
	 * set for undefined its dont need to cal it
	 */
	addXYIfValid(x, y){ 
		this.addXIfValid(x);
		this.addYIfValid(y);
		return this;
	}
	/**
	 * 
	 * @param {Vector2DType} other vector object
	 */
	addVectorIfValid(other){
		let other_vector = Vector2D.evalVector(other);
		if(!_.isNull(other_vector)){
			this.addXYIfValid(other_vector.x, other_vector.y);
		}
		return this;
	}
	/**
	 * 
	 * @param {*} x any value, hoped x to substract from value
	 * substracts x from current x value
	 */
	subX(x){ this.__x -= Vector2D._evalSafe(x); return this;}
		/**
	 * 
	 * @param {*} y any value, hoped y to subtract from value
	 * subtract y from current y value
	 */
	subY(y){
		this.__y -=  Vector2D._evalSafe(y);
		return this;
	}
	/**
	 * 
	 * @param {*} x any value, hoped number to subtract from value
	 * @param {*} y any value, hoped number to subtract from value
	 * substracts x from vector.x and y from vector.y, except if the specific values (x, y) are undefined
	 */
	subXY(x, y) {
		__vector2ArgsOperationWrapper(this, this.subX, x);
		__vector2ArgsOperationWrapper(this, this.subY, y);
		return this;
	}
	/**
	 * 
	 * @param {Vector2DType} other other object
	 * @returns {Vector2DType} other other object
	 * evaluates the other object as Vector2D, then substracts
	 */
	subVector(other) {
		let other_vector = Vector2D.evalVector(other);
		this.subXY(other_vector.x, other_vector.y);
		return this;
	}
	/**
	 * @param {*} x any value hoped to be a number
	 * @returns {*} any value if 
	 */
	subIfValidX(x){ this.setXIfValid(this.__x - Vector2D._evalSafe(x)) }
	subIfValidY(y){ this.setYIfValid(this.__y - Vector2D._evalSafe(y)) }
	subIfValidXY(x, y){ 
		this.subIdValidX(x);
		this.subIfValidY(y);
		return this;
	}
	subIfValidVector(other){
		let other_vector = Vector2D.evalVector(other);
		if(!_.isNull(other_vector)){
			this.subIfSafeXY(other_vector.x, other_vector.y);
		}
		return this;
	}
	/**
	 * 
	 * @param {*} mul any value hoping to be a number
	 * multiples this.x by mul, if mul isnt a number its setted to NaN
	 */
	mulX(mul){
		this.__x *= Vector2D._evalSafe(mul);
		return this;
	}
	mulY(mul){
		this.__y *= Vector2D._evalSafe(mul);
		return this;
	}
	mulXY(mul, mul2){
		if(_.isUndefined(mul2)){
			mul2 = mul;
		}
		__vector2ArgsOperationWrapper(this, this.mulX, mul);
		__vector2ArgsOperationWrapper(this, this.mulX, mul2);
		return this;
	}
	safeMulX(mul){
		this.setXIfValid(this.__x * Vector2D._evalSafe(mul));
		return this;
	}
	safeMulY(mul){
		this.setYIfValid(this.__y * Vector2D._evalSafe(mul));
		return this;
	}
	safeMulXY(mul, mul2){
		if(_.isUndefined(mul2)){
			mul2 = mul;
		}
		__vector2ArgsOperationWrapper(this, this.safeMulY, mul);
		__vector2ArgsOperationWrapper(this, this.safeMulX, mul2);
		return this;
	}
	/**
	 * 
	 * @param {*} div number to div y
	 * @returns {Vector} this
	 */
	divX(div){
		this.__x /= Vector2D._evalSafe(div);
		return this;
	}
	/**
	 * 
	 * @param {*} div number to div y
	 * @returns {Vector} this
	 */
	divY(div){
		this.__y /= Vector2D._evalSafe(div);
		return this;
	}
	/**
	 * 
	 * @param {*} div  number to div
	 * @param {*} div2 number to div2
	 * @returns {Vector} this
	 * div X and Y by numbers,if they aren't numbers divide by NaN, if div2 is undefined divides both by div2
	 */
	divXY(div, div2){
		if(_.isUndefined(div2)){
			div2 = div;
		}
		__vector2ArgsOperationWrapper(this, this.divX, div);
		__vector2ArgsOperationWrapper(this, this.divY, div2);
		return this;
	}
	/**
	 * 
	 * @param {*} div hopefully a number to divide x
	 * @returns {Vector} this
	 * divides x if not safe
	 */
	safeDivX(div){
		this.setXIfValid(this.__x / Vector2D._evalSafe(div));
		return this;
	}
	/**
	 * @param {*} div hopefully a number to divide y
	 * @return {Vector} vector
	 */
	safeDivY(div){
		this.setYIfValid(this.__y / Vector2D._evalSafe(div));
		return this;
    }
    /**
     * 
     * @param {*} div anything hoping to be a number to divide
     * @param {*} div2 anything hoping to be a number
	 * @return {Vector} vector
     */
	safeDivXY(div, div2){
		if(_.isUndefined(div2)){
			div2 = div;
		}
		this.safeDivX(this, this.safeDivY, div);
		this.safeDivY(this, this.safeDivX, div2);
		return this;
	}
	/**
	 * @return {Vector} vector
	 */
	neg(){
		return new Vector2D(-this.__x, -this.__y);
	}
	/**
	 * clones the vector as new object, to prevent 
	 * @returns {Vector} clone of this object
	 */
	clone(){
		return new Vector2D(this.__x, this.__y);
	}
	/**
	 * @returns {string} a string representing of the instance
	 */
	toString(){
		return `Vector2D[${this.x},${this.y}]`;
	}
	/**
	 * @param {Vector2DType} other other object
	 * @returns {boolean} if equals to current vector
	 * the first checks if other is valid vector (if so returns null) otherwise compares the x and y 
	 */
	equals(other){
		// evaluate the objects as arrays
		let other_vector = Vector2D.evalVector(other);
		if(_.isNull(other_vector)){
			return false;
		}
		// else
		return this.__x == other_vector.x && this.__y == other_vector.__y
	}
	/**
	 * @returns array representation of the 2d vector
	 * just returns the vector as array
	 */
	array() {
		return [this.x, this.y]
	}
	/**
	 * @returns {boolean} if vector is zero
	 * vector zero means empty value, used in statements
	 */
	isZero(){
		return !this.equals(Vector2D.zero());
    }
    /**
     * @returns {boolean} if vector isNaN
     * a vector is nan if either x or y of the vector are NaN
     */
	isNaN(){
		return isNaN(this.__x) || isNaN(this.__y);
	}
}