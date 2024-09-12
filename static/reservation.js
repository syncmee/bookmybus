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