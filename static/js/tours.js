// tours.js

document.addEventListener('DOMContentLoaded', function() {
    var slides = document.querySelectorAll('.slideshow-background img');
    var currentSlide = 0;
    var slideInterval = setInterval(nextSlide, 6000); // Change slide every 6 seconds
  
    function nextSlide() {
      slides[currentSlide].classList.remove('active');
      currentSlide = (currentSlide + 1) % slides.length;
      slides[currentSlide].classList.add('active');
    }
  });
  