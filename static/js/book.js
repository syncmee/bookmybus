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
