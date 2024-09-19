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
