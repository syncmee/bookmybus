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
        dateFormat: "F j, Y",
        minDate: "today"// Custom Flatpickr options here
    });

    calendarIcon.addEventListener('click', function() {
        dateInput._flatpickr.open(); // Open Flatpickr date picker
    });
});
