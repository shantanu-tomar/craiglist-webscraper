
			
function Theme() {
	let button = document.getElementById('theme_toggle');
	document.getElementById('theme').className = button.innerHTML;
	sessionStorage.setItem("theme", button.innerHTML);
	
	if (button.innerHTML == 'Light') {
		button.innerHTML = 'Dark';
	}
	else {
		button.innerHTML = 'Light';
	}
	sessionStorage.setItem("theme_toggle", button.innerHTML);
	
}


		
function Radio(radio, id) {
	document.getElementById('sort_param').value = radio;
	sessionStorage.setItem('radio_id', id)
	}
	
function SubmitSearch() {
	sessionStorage.setItem('price_min', document.getElementById('price_min').value);
	sessionStorage.setItem('price_max', document.getElementById('price_max').value);
	let query = document.getElementById('textbox').value;
	if ( query=='' ) {
		query_stored = sessionStorage.getItem('query');
		document.getElementById('textbox').value = query_stored;
		if (query_stored != '') {
			document.getElementById('new_search').submit();
		}
		else {
			alert("That's not a valid search !");
		}
	}
}

function CardSubmit(id) {
	let card_id = 'card_'.concat(id);
	document.getElementById(card_id).submit();
}

let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slides[slideIndex-1].style.display = "block";
}