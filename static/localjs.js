console.log('js janjian');
const queryString = window.location.search;
var formaddfo = document.getElementById('formaddfo');


if (queryString){
    console.log(queryString);
} else{
    console.log('no param');
    formaddfo.style.display = 'none';
}