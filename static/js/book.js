// <!-- JavaScript for seat selection -->

function selectSeat(seat) {
if (seat.classList.contains('booked')) {
  return; // Ignore clicks on booked seats
}
seat.classList.toggle('selected');
}

function selectSleeper(sleeper) {
  if (sleeper.classList.contains('booked')) {
    return; // Ignore clicks on booked seats
  }
  sleeper.classList.toggle('selected');
}

// Function to select a seat
function selectSeat(seat) {
  if (seat.classList.contains('booked')) {
    return; // Ignore clicks on booked seats
  }
  seat.classList.toggle('selected');
  updateSeatCount();  // Update seat count after selection
}

// Function to select a sleeper (if applicable)
function selectSleeper(sleeper) {
  if (sleeper.classList.contains('booked')) {
    return; // Ignore clicks on booked sleepers
  }
  sleeper.classList.toggle('selected');
  updateSeatCount();  // Update seat count after selection
}

// Function to count selected seats
function updateSeatCount() {
  const selectedSeats = document.querySelectorAll('.seat.selected'); // Get all selected seats
  const seatCount = selectedSeats.length; // Count the selected seats
  console.log(seatCount);  // You can log this or display it somewhere in your UI

  // Optionally display the count somewhere in the modal
  document.getElementById('seatCount').textContent = seatCount;
  document.getElementById('seatCountmodal').textContent = seatCount;
}

// seatSelection.js

function updateSeatCount() {
  // Get seat price from the data attribute in the HTML
  const seatPrice = document.getElementById('seatPrice').getAttribute('data-seat-price');

  const selectedSeats = document.querySelectorAll('.seat.selected'); // Get all selected seats
  const seatCount = selectedSeats.length; // Count the selected seats

  // Update seat count display
  document.getElementById('seatCount').textContent = seatCount;
  document.getElementById('seatCountmodal').textContent = seatCount;

  // Calculate and update total price
  const totalPrice = seatCount * seatPrice;
  document.getElementById('totalPrice').textContent = `₹${totalPrice}`;
}

function updateTotalPrice(newPrice) {
    const totalPriceElement = document.getElementById('totalPrice');
    const totalPriceInput = document.getElementById('totalPriceInput');

    totalPriceElement.textContent = newPrice.toFixed(2); // Update displayed price
    totalPriceInput.value = newPrice.toFixed(2); // Update hidden input for form submission
}

// Example of calling this function when seat selection changes
// updateTotalPrice(newCalculatedPrice);
let selectedSeats = [];  // Array to store selected seat numbers
let seatPrice = parseInt(document.getElementById('seatPrice').dataset.seatPrice);  // Fetch seat price from modal

function selectSeat(seat) {
    if (seat.classList.contains('booked')) {
        return;  // Ignore clicks on booked seats
    }

    let seatNumber = seat.id.split('_')[1];  // Get seat number from the seat's ID

    // Toggle seat selection
    if (seat.classList.contains('selected')) {
        seat.classList.remove('selected');
        selectedSeats = selectedSeats.filter(s => s !== seatNumber);  // Remove from selected seats
    } else {
        seat.classList.add('selected');
        selectedSeats.push(seatNumber);  // Add to selected seats
    }

    // Update the selected seats count and total price
    let seatCount = selectedSeats.length;
    let totalPrice = seatCount * seatPrice;

    document.getElementById('seatCountmodal').innerText = seatCount;  // Update the modal seat count
    document.getElementById('totalPrice').innerText = totalPrice;  // Update the total price display
    document.getElementById('totalPriceInput').value = totalPrice;  // Update hidden input value

    // Update the hidden fields for form submission
    document.getElementById('selectedSeats').value = selectedSeats.join(', ');  // Store selected seats as a comma-separated string
    document.getElementById('selectedSeatCount').value = seatCount;  // Store the seat count
}
