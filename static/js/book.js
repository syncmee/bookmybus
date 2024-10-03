// Function to select a seat
function selectSeat(seat) {
  if (seat.classList.contains('booked')) {
    return; // Ignore clicks on booked seats
  }
  seat.classList.toggle('selected');
  updateSeatCount();  // Update seat count and selected seats after selection
}

// Function to count selected seats and update total price and selected seats
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
  // Update the hidden input field value to match the total price
  document.getElementById('totalPriceInput').value = totalPrice; // Set the hidden input value

  // Get selected seat numbers
  const selectedSeatNumbers = Array.from(selectedSeats).map(seat => seat.id.split('_')[1]).join(','); // Extract seat numbers
  document.getElementById('selectedSeatsInput').value = selectedSeatNumbers; // Update the hidden input for selected seats
  document.getElementById('selectedSeatCount').value = seatCount; // Update the hidden input for selected seat count
}

// Function to validate seat selection before form submission
function validateSeatSelection(event) {
  const selectedSeats = document.querySelectorAll('.seat.selected');
  if (selectedSeats.length === 0) {
    event.preventDefault(); // Prevent form submission
    alert('Please select at least one seat before submitting the form.'); // Alert the user
  }
}
