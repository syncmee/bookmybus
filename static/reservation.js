const cities = ['Delhi', 'Mumbai', 'Bengaluru', 'Chennai', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam', 'Patna', 'Vadodara', 'Chandigarh', 'Coimbatore', 'Kochi', 'Guwahati', 'Amritsar', 'Jodhpur', 'Agra'];

function showSuggestions(inputElement, type) {
    const query = inputElement.value.toLowerCase();
    const suggestionsBox = document.getElementById(`${type}-suggestions`);

    // Clear previous suggestions
    suggestionsBox.innerHTML = '';

    if (query.length > 0) {
        // Filter the cities based on input
        const filteredCities = cities.filter(city => city.toLowerCase().includes(query));

        // Show filtered options
        filteredCities.forEach(city => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'autocomplete-item';
            suggestionItem.textContent = city;
            suggestionItem.onclick = function() {
                inputElement.value = city; // Set input value to the selected city
                suggestionsBox.innerHTML = ''; // Clear suggestions
                suggestionsBox.style.display = 'none'; // Hide suggestions box
            };
            suggestionsBox.appendChild(suggestionItem);
        });

        suggestionsBox.style.display = 'block'; // Show suggestions
    } else {
        suggestionsBox.style.display = 'none'; // Hide suggestions if input is empty
    }
}

// Close suggestions if clicked outside
document.addEventListener('click', function(event) {
    const fromSuggestions = document.getElementById('from-suggestions');
    const toSuggestions = document.getElementById('to-suggestions');
    if (!event.target.closest('#from-destination')) {
        fromSuggestions.style.display = 'none';
    }
    if (!event.target.closest('#to-destination')) {
        toSuggestions.style.display = 'none';
    }
});

const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, '0'); // Month starts from 0, so add 1
const day = String(today.getDate()).padStart(2, '0'); // Add leading zero if necessary

// Format date as YYYY-MM-DD
const formattedDate = `${year}-${month}-${day}`;

// Set the value of the date input to today's date
document.getElementById('date-input').value = formattedDate;

// Add a 2-second delay before removing the loading screen
window.addEventListener("load", function() {
  setTimeout(function() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('content').style.display = 'block';
  }, 2000); // 2000ms = 2 seconds
});

document.addEventListener('DOMContentLoaded', function() {
    var calendarIcon = document.getElementById('calendar-icon');
    var dateInput = document.getElementById('date-input');

    flatpickr(dateInput, {
//        altInput: true,
//        altFormat: "d m, Y",
//        dateFormat: "Y-m-d",
        minDate: "today"// Custom Flatpickr options here
    });

    calendarIcon.addEventListener('click', function() {
        dateInput._flatpickr.open(); // Open Flatpickr date picker
    });
});
