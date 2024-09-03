// Pure JavaScript Implementation
// var menuIcon = document.querySelector('.menu-icon');
// var sideBar = document.querySelector('.side-bar');

// menuIcon.onclick = function(){
//     sideBar.classList.toggle('small-sidebar');
// }


// jQuery Implementation
$(function(){
    $('.menu-icon').on('click', () => {
        $('.side-bar').toggleClass('small-sidebar')
    });
});