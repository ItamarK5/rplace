/**
 * @auther Itamar Kanne
 * @file all files and includes all javascript code of the meme page
 */


/**
 * @param {HTMImageElement} image image displayed the meme
 */
const fix_size = (image) => {
	// prefer min length to prevent overflow;
	let max_height = Math.floor(parseFloat(window.innerHeight) - parseFloat($('#text-container').css('height').slice(0,-2)));
	let image_height = $(image).css('height').slice(0, -2);
	if(max_height < image_height){
		$(image).css(
		    'height',
			`min(${max_height}px, ${image_height}px)`
		);
	} 
};

/**
 * @desc fixes the size of the image
 * @param {HTMImageElement} image image displayed the meme
 * @see {@link http://kimjoyfox.com/using-jquery-to-resize-images-after-loading/}
 */
const waitToFixImageSize = (image) => {
	if(image.complete){
		fix_size(image);
	} else { $(image).on('load', () => fix_size(image)) }
}

// ready
$(document).ready(function() {
	let meme_image = $('#meme-image')[0];
	waitToFixImageSize(meme_image)
	$(window).resize(
		waitToFixImageSize(meme_image)
	);
});
