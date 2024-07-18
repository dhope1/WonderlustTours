document.addEventListener('DOMContentLoaded', function() {
  var slides = document.querySelectorAll('.slideshow-background img');
  var currentSlide = 0;
  var slideInterval = setInterval(nextSlide, 7000); // Change slide every 4 seconds

  function nextSlide() {
      slides[currentSlide].classList.remove('active');
      currentSlide = (currentSlide + 1) % slides.length;
      slides[currentSlide].classList.add('active');
  }

  var tours = [
      { id: 1, title: "Tour 1", description: "Explore the romantic streets of Paris", price: 100, location: "Europe", image_filename: "paris.jpg" },
      { id: 2, title: "Tour 2", description: "Discover the vibrant culture of London", price: 200, location: "Europe", image_filename: "london.jpg" },
      { id: 3, title: "Tour 3", description: "Experience the rich history of Rome", price: 150, location: "Europe", image_filename: "rome.jpg" },
      { id: 4, title: "Tour 4", description: "Relax on the beaches of Bali", price: 300, location: "Asia", image_filename: "bali.jpg" },
      { id: 5, title: "Tour 5", description: "Discover the bustling city of Tokyo", price: 250, location: "Asia", image_filename: "tokyo.jpg" },
      { id: 6, title: "Tour 6", description: "Visit the temples of Angkor Wat", price: 550, location: "Asia", image_filename: "angkor_wat.jpg" },
      { id: 7, title: "Tour 7", description: "Experience the magic of Disney World", price: 350, location: "North America", image_filename: "disney.jpg" },
      { id: 8, title: "Tour 8", description: "Adventure through the wilds of Alaska", price: 500, location: "North America", image_filename: "alaska.jpg" },
      { id: 9, title: "Tour 9", description: "Take a wine tour in Napa Valley", price: 500, location: "North America", image_filename: "napa_valley.jpg" },
      { id: 10, title: "Tour 10", description: "Safari in the Serengeti", price: 600, location: "Africa", image_filename: "safari.jpg" },
      { id: 11, title: "Tour 11", description: "Explore the pyramids of Egypt", price: 600, location: "Africa", image_filename: "pyramids.jpg" },
      { id: 12, title: "Tour 12", description: "Relax on the beaches of Seychelles", price: 400, location: "Africa", image_filename: "seychelles.jpg" },
      { id: 13, title: "Tour 13", description: "Dive in the Great Barrier Reef", price: 800, location: "Australia", image_filename: "reef.jpg" },
      { id: 14, title: "Tour 14", description: "Tour the Outback of Australia", price: 600, location: "Australia", image_filename: "outback.jpg" },
      { id: 15, title: "Tour 15", description: "Explore the cultural landmarks of Sydney", price: 350, location: "Australia", image_filename: "sydney.jpg" },
      { id: 16, title: "Hike the Inca Trail to Machu Picchu", description: "Hike the Inca Trail to Machu Picchu", price: 700, location: "South America", image_filename: "machu_picchu.jpg" },
      { id: 17, title: "Relax on the beaches of Rio de Janeiro", description: "Relax on the beaches of Rio de Janeiro", price: 450, location: "South America", image_filename: "rio.jpg" },
      { id: 18, title: "Explore the Amazon rainforest", description: "Explore the Amazon rainforest", price: 650, location: "South America", image_filename: "amazon.jpg" },
      { id: 19, title: "Cruise through the fjords of Norway", description: "Cruise through the fjords of Norway", price: 400, location: "Europe", image_filename: "norway.jpg" },
      { id: 20, title: "Tour the castles of Scotland", description: "Tour the castles of Scotland", price: 450, location: "Europe", image_filename: "scotland.jpg" },
      { id: 21, title: "Explore the islands of Greece", description: "Explore the islands of Greece", price: 400, location: "Europe", image_filename: "greece.jpg" },
      { id: 22, title: "Experience the nightlife of Ibiza", description: "Experience the nightlife of Ibiza", price: 300, location: "Europe", image_filename: "ibiza.jpg" },
      { id: 23, title: "Visit the museums of Berlin", description: "Visit the museums of Berlin", price: 250, location: "Europe", image_filename: "berlin.jpg" },
      { id: 24, title: "Walk the streets of Havana", description: "Walk the streets of Havana", price: 200, location: "North America", image_filename: "havana.jpg" },
      { id: 25, title: "Tour the castles of Canada", description: "Tour the castles of Canada", price: 450, location: "North America", image_filename: "canada.jpg" },
      { id: 26, title: "Cruise the Caribbean", description: "Cruise the Caribbean", price: 700, location: "Caribbean", image_filename: "caribbean.jpg" },
      { id: 27, title: "Relax on the beaches of the Bahamas", description: "Relax on the beaches of the Bahamas", price: 500, location: "Caribbean", image_filename: "bahamas.jpg" },
      { id: 28, title: "Explore the wildlife of Madagascar", description: "Explore the wildlife of Madagascar", price: 500, location: "Africa", image_filename: "madagascar.jpg" },
      { id: 29, title: "Discover the history of Jerusalem", description: "Discover the history of Jerusalem", price: 350, location: "Asia", image_filename: "jerusalem.jpg" },
      { id: 30, title: "Experience the culture of Mumbai", description: "Experience the culture of Mumbai", price: 250, location: "Asia", image_filename: "mumbai.jpg" }
  ];

  function displayTours(filteredTours) {
      var tourList = document.getElementById('tourList');
      tourList.innerHTML = ''; // Clear existing tours

      filteredTours.forEach(function(tour) {
          var tourCard = `
              <div class="col-md-4">
                  <div class="card mb-4">
                      <img src="${baseURL}${tour.image_filename}" class="card-img-top" alt="${tour.title}">
                      <div class="card-body">
                          <h5 class="card-title">${tour.title}</h5>
                          <p class="card-text">${tour.description.substring(0, 100)}...</p>
                          <a href="/tour/${tour.id}" class="btn btn-primary">View Details</a>
                      </div>
                  </div>
              </div>`;
          tourList.innerHTML += tourCard;
      });
  }

  function filterTours() {
      var filterPrice = document.getElementById('filterPrice').value;
      var filterLocation = document.getElementById('filterLocation').value.toLowerCase();

      var filteredTours = tours.filter(function(tour) {
          var matchesPrice = filterPrice ? tour.price <= filterPrice : true;
          var matchesLocation = filterLocation ? tour.location.toLowerCase().includes(filterLocation) : true;
          return matchesPrice && matchesLocation;
      });

      displayTours(filteredTours);
  }

  var btnApplyFilters = document.getElementById('btnApplyFilters');
  btnApplyFilters.addEventListener('click', filterTours);

  // Initially display all tours
  displayTours(tours);
});
