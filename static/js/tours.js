document.addEventListener('DOMContentLoaded', function() {
  // Slideshow functionality
  var slides = document.querySelectorAll('.slideshow-background img');
  var currentSlide = 0;
  var slideInterval = setInterval(nextSlide, 7000); // Change slide every 7 seconds

  function nextSlide() {
      slides[currentSlide].classList.remove('active');
      currentSlide = (currentSlide + 1) % slides.length;
      slides[currentSlide].classList.add('active');
  }

  // Base URL for images
  const baseURL = '/static/images/'; // Assuming your images are served from this path

  // Function to fetch tours from the server
  async function fetchTours() {
      try {
          const response = await fetch('/api/tours');
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return await response.json(); // Return the fetched tours
      } catch (error) {
          console.error('Fetch error:', error);
          return []; // Return an empty array in case of an error
      }
  }

  // Function to display tours
  function displayTours(tours) {
      const tourList = document.getElementById('tourList');
      tourList.innerHTML = ''; // Clear existing tours

      tours.forEach(function(tour) {
          const tourCard = `
              <div class="col-md-4">
                  <div class="card mb-4">
                      <img src="${baseURL}${tour.image_filename}" class="card-img-top" alt="${tour.title}">
                      <div class="card-body">
                          <h5 class="card-title">${tour.title}</h5>
                          <p class="card-text">${tour.description.substring(0, 100)}...</p>
                          <a href="/book/${tour.id}" class="btn btn-primary">Book Here</a>
                      </div>
                  </div>
              </div>`;
          tourList.innerHTML += tourCard;
      });
  }

  // Function to filter tours based on user input
  function filterTours(tours) {
      const filterPrice = parseFloat(document.getElementById('filterPrice').value) || Infinity;
      const filterLocation = document.getElementById('filterLocation').value.toLowerCase();

      const filteredTours = tours.filter(function(tour) {
          const matchesPrice = tour.price <= filterPrice;
          const matchesLocation = tour.location.toLowerCase().includes(filterLocation);
          return matchesPrice && matchesLocation;
      });

      displayTours(filteredTours);
  }

  // Event listener for filter button
  document.getElementById('btnApplyFilters').addEventListener('click', async function() {
      const tours = await fetchTours();
      filterTours(tours);
  });

  // Initially fetch and display all tours
  fetchTours().then(tours => displayTours(tours));
});
