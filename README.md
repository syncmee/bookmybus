
![Logo](https://github.com/syncmee/bookmybus/blob/main/static/logos/bmb_logo.png?raw=true)

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue)
[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://github.com/syncmee/)
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rohittalukdar)

# BookMyBus

BookMyBus is a web application that allows users to search and book bus tickets. It features an intuitive user interface for selecting buses, booking seats, and managing travel itineraries. This project is built using Python, Flask, and MDBootstrap, with an emphasis on user authentication, seat selection, and real-time bus availability.

## Features

- **Bus Search**: Search buses by routes, timings, and availability.
- **Seat Selection**: Interactive seat selection modal to choose available seats.
- **User Authentication**: Secure login system with 'Remember Me' functionality and **OAuth support** (Google, GitHub, Twitter).
- **Real-time Updates**: Bus availability and seat booking in real-time.
- **24-Hour Time Format**: Departure and arrival times displayed in 24-hour format, with a hover-over explanation for next-day arrivals.
- **Date Picker Integration**: Flatpickr date picker integrated with a custom calendar icon for easy date selection.
- **Booking History**: View past bookings and upcoming trips in the user dashboard.

## Tech Stack

**Client:** MDBootstrap (MDB), HTML, CSS, JavaScript

**Server:** Python (Flask), PostgreSQL

**Deployment:** Railway.io

## Installation

[![Install Now](https://img.shields.io/badge/install-now-green.svg)](https://github.com/syncmee/bookmybus)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/syncmee/bookmybus.git
   ```
2. **Navigate to the project directory**: 
   ```bash
   cd bookmybus
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app**:
   ```bash
   flask run
   ```

## Demo

![BookMyBus Demo](path-to-demo/demo.gif)

_Example of searching for buses and selecting seats_

## Flow Map for BookMyBus

**1. User Journey**  
Start: User Opens the App  

**User Authentication**:
- Login/Signup Page
- User can log in via credentials or use **OAuth** for Google, GitHub, or Twitter.
- If the user selects "Remember Me," a session is stored.
- Credentials are validated via the backend (Flask + PostgreSQL).
- If invalid, display an error message.
- If valid, redirect to the dashboard.

**Search Buses**:
- User enters:
  - Departure City
  - Destination City
  - Date of Journey (via Flatpickr Date Picker)
- Backend fetches available buses based on the search criteria from the database.
- Results display in a list with:
  - Bus Names
  - Timings (in 24-hour format)
  - Availability Status
  - Price

**Bus Selection**:
- User selects a bus.
- The system shows:
  - Bus Details (Seats, Timing, Amenities, etc.)
  - Seat Layout (Available/Booked seats indicated)
  - Real-time seat availability (Seats update in real-time)

**Seat Selection**:
- User selects their seat(s).
- The system updates the UI to mark selected seats and lock them temporarily.
- The system checks:
  - If selected seats are still available.
  - If unavailable, display a message.
  - If available, proceed.

**Booking Confirmation**:
- User confirms the booking.
- User provides personal and payment details.
- Payment Gateway Interaction (optional in this flow map).
- Backend processes the booking:
  - Updates the seat status in the database.
  - Generates a booking confirmation.
  - Redirects to the booking success page.

**Booking History**:
- User is redirected to the Dashboard showing:
  - Upcoming trips.
  - Booking history.
  - Cancellation option (if allowed).

**2. Backend Processes**  

**Database Interaction (PostgreSQL)**:
- Bus Search: Fetch available buses based on route and date.
- Seat Availability Check: Query the database to check which seats are available or booked.
- User Authentication: Validate login credentials and handle OAuth.
- Booking Confirmation: Update the seat booking status and store user booking information.

**Session Management**:
- The system manages user sessions for authenticated users and handles session timeouts.
- If "Remember Me" is checked, the user’s session lasts longer until they log out manually.

## Contributing

Contributions are always welcome! Feel free to fork this project, make improvements, and submit a pull request. For major changes, please open an issue first.
