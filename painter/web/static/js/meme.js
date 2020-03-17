const fix_size = (image) => {
    // prefer min length to prevent overflow;
    let max_height = Math.floor(parseFloat(window.innerHeight) - parseFloat($('#text-container').css('height').slice(0,-2)));
    let image_height = $(image).css('height').slice(0, -2);
    console.log(image_height, max_height)
    if(max_height < image_height){
        $(image).css(
            'height',
            `min(${max_height}px, ${image_height}px)`
        );
    } 
};

//http://kimjoyfox.com/using-jquery-to-resize-images-after-loading/
const wait_to_fix_image_size = (image) => {
    if(image.complete){
        fix_size(image);
    } else { $(image).on('load', () => fix_size(image)) }
}

$(document).ready(function() {
    let meme_image = $('#meme-image')[0];
    wait_to_fix_image_size(meme_image)
    $(window).resize(
        wait_to_fix_image_size(meme_image)
    );
});
