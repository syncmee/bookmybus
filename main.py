from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, random
import requests
import gunicorn
import ast
import os
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Necessary for session management

# Email-Setup
mail = 'bookmybus.info@gmail.com'
mail_password = 'qprp xuxk gaml bdca'

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized access

# Destinations for Ticket-Booking
VALID_DESTINATIONS = {
    'from': ["Agra", "Mumbai", "Jaipur", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
             "Kolkata", "Goa", "Varanasi", "Udaipur", "Amritsar", "Jaisalmer", "Mysore",
             "Pune", "Rishikesh", "Leh", "Ladakh", "Kochi", "Ooty", "Darjeeling", "Shimla",
             "Manali", "Kaziranga", "Khajuraho", "Ranthambore"],
    'to': ["Agra", "Mumbai", "Jaipur", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
           "Kolkata", "Goa", "Varanasi", "Udaipur", "Amritsar", "Jaisalmer", "Mysore",
           "Pune", "Rishikesh", "Leh", "Ladakh", "Kochi", "Ooty", "Darjeeling", "Shimla",
           "Manali", "Kaziranga", "Khajuraho", "Ranthambore"]
}

# Mapbox API key
api_key = 'pk.eyJ1Ijoic3luY21lIiwiYSI6ImNtMTNrdzdzdzB2YXIyanMxaHMzZmZzamwifQ.8KxUY8AEe-zwc8ACUmEWtw'

# Define city coordinates for Mapbox Directions API
city_coordinates = {
    "Agra": {"lat": 27.1767, "lon": 78.0081},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739},
    "Udaipur": {"lat": 24.5854, "lon": 73.7125},
    "Amritsar": {"lat": 31.6340, "lon": 74.8723},
    "Jaisalmer": {"lat": 26.9157, "lon": 70.9083},
    "Mysore": {"lat": 12.2958, "lon": 76.6394},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Rishikesh": {"lat": 30.0869, "lon": 78.2676},
    "Leh": {"lat": 34.1526, "lon": 77.5770},
    "Ladakh": {"lat": 34.2268, "lon": 77.5619},
    "Kochi": {"lat": 9.9312, "lon": 76.2673},
    "Ooty": {"lat": 11.4064, "lon": 76.6932},
    "Darjeeling": {"lat": 27.0360, "lon": 88.2627},
    "Shimla": {"lat": 31.1048, "lon": 77.1734},
    "Manali": {"lat": 32.2396, "lon": 77.1887},
    "Kaziranga": {"lat": 26.5775, "lon": 93.1711},
    "Khajuraho": {"lat": 24.8318, "lon": 79.9199},
    "Ranthambore": {"lat": 26.0173, "lon": 76.5026}
}

# Function to get distance and duration from Mapbox Directions API
def get_distance_mapbox(api_key, origin, destination):
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin};{destination}"

    params = {
        'access_token': api_key,
        'geometries': 'geojson',
        'overview': 'full',
        'steps': 'true'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'routes' in data and len(data['routes']) > 0:
        duration = data['routes'][0]['duration']
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        duration_str = f"{hours} hr {minutes} min" if hours > 0 else f"{minutes} min"
        return duration_str
    return "No route found"
from datetime import datetime, timedelta

def adjust_arrival_time(departure_time_str, travel_time_str):
    # Parse departure time assuming it's provided in 24-hour format
    departure_time = datetime.strptime("2024-01-01 " + departure_time_str, "%Y-%m-%d %H:%M")

    # Parse travel time
    travel_time_parts = travel_time_str.split()
    hours = int(travel_time_parts[0].replace("hr", "")) if "hr" in travel_time_parts else 0
    minutes = int(travel_time_parts[-2].replace("min", "")) if "min" in travel_time_parts else 0
    travel_duration = timedelta(hours=hours, minutes=minutes)

    # Calculate arrival time
    arrival_time = departure_time + travel_duration

    # Format departure and arrival times in 24-hour format
    departure_time_str_24 = departure_time.strftime("%H:%M")
    arrival_time_str_24 = arrival_time.strftime("%H:%M")

    day_difference = (arrival_time.date() - departure_time.date()).days

    # Check if arrival is on the next day
    next_day_indicator = ""
    if day_difference == 1:
        next_day_indicator = "+1"
    elif day_difference == 2:
        next_day_indicator = "+2"
    elif day_difference == 3:
        next_day_indicator = "+3"

    return departure_time_str_24, arrival_time_str_24, next_day_indicator

# Example usage
departure_time_str = "23:00"  # 24-hour format input
travel_time_str = "2 hr 30 min"
departure_24, arrival_24, next_day = adjust_arrival_time(departure_time_str, travel_time_str)
print(f"Departure Time: {departure_24}")
print(f"Arrival Time: {arrival_24} {next_day}")



# User model for SQLAlchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('recipient-name')
        subject = request.form.get('subject')
        email = request.form.get('email')
        message = request.form.get('message-text')

        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=mail, password=mail_password)
            connection.sendmail(from_addr=mail,
                                to_addrs=email,
                                msg=f"Subject: [BookMyBus Customer Support] - {subject} \n\n"
                                    f"##- Please type your reply above this line -##\n"
                                    f"Hey {name},\nThanks for reaching out to us\n"
                                    f"{name}: {message}\n"
                                    f"Soon Our Support Team Will Get Back To You Under This Thread. \n\n"
                                    f"Thank you for choosing Book My Bus"
                                )
    return render_template('homepage.html')

@app.route('/test')
def test():

    return render_template('test.html', )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check if it's a registration or login submission
        if 'signup-username' in request.form:
            # Registration logic
            name = request.form['signup-name']
            username = request.form['signup-username']
            email = request.form['signup-email']
            password = request.form['signup-password']

            # Check if the username or email already exists
            if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
                flash('Username or Email already exists. Please try a different one!', 'danger')
                return redirect(url_for('login'))
            else:
                # Hash the password before storing it
                hashed_password = generate_password_hash(password)
                # Add the new user to the database
                new_user = User(name=name, username=username, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                # Redirect to the dashboard route with the username parameter
                return redirect(url_for('dashboard', user=name))

        elif 'username' in request.form:
            input_data = request.form['username']  # This could be either username or email
            password = request.form['password']

            # Determine if input is username or email
            user = User.query.filter((User.username == input_data) | (User.email == input_data)).first()

            if user and check_password_hash(user.password, password):
                login_user(user)  # Log the user in
                # Redirect to the dashboard route with the user's name
                return redirect(url_for('dashboard', user=user.name))
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return redirect(url_for('login'))

    return render_template('sign-up.html')

@app.route('/dashboard/<user>', methods=['GET', 'POST'])
@login_required
def dashboard(user):
    if request.method == 'POST':
        from_destination = request.form.get('from-destination').title()
        to_destination = request.form.get('to-destination').title()
        travel_date = request.form.get('travel-date')

        if from_destination not in VALID_DESTINATIONS['from']:
            flash('Please select a valid city from the "From" dropdown menu.', 'danger')
            return redirect(url_for('dashboard', user=user))

        if to_destination not in VALID_DESTINATIONS['to']:
            flash('Please select a valid city from the "To" dropdown menu.', 'danger')
            return redirect(url_for('dashboard', user=user))

        if to_destination == from_destination:
            flash('Please select a different city.', 'danger')
            return redirect(url_for('dashboard', user=user))

        # Get latitude/longitude coordinates for the cities
        origin = f"{city_coordinates[from_destination]['lon']},{city_coordinates[from_destination]['lat']}"
        destination = f"{city_coordinates[to_destination]['lon']},{city_coordinates[to_destination]['lat']}"

        # Get the travel time using Mapbox Directions API
        travel_time = get_distance_mapbox(api_key, origin, destination)

        # Example departure times in 24-hour format
        departure_times = ['06:00','10:30','08:15','18:00', '16:45', '19:15']  # List of departure times for each bus

        # Define the bus list dynamically inside the route
        buses = []
        for departure_time in departure_times:
            # Calculate the arrival time
            departure_24, arrival_24, next_day = adjust_arrival_time(departure_time, travel_time)
            # Define bus types based on departure time
            if departure_time == '06:00' or departure_time == '18:00':
                bus_type = 'Sleeper'; price = '₹' + str(random.choice(range(1701,3000)))
            elif departure_time == '10:30' or departure_time == '16:45':
                bus_type = 'AC'; price = '₹' + str(random.choice(range(1001,1700)))
            elif departure_time == '08:15' or departure_time == '19:15':
                bus_type = 'Non-AC'; price = '₹' + str(random.choice(range(700,1400)))

            bus = {
                'busline': 'BookMyBus',
                'departure_time': departure_24,  # Use the 24-hour format departure time
                'arrival_time': [arrival_24.strip(), next_day.strip()],  # Format arrival time with next day indicator
                'duration': travel_time,
                'to': to_destination,
                'price': price,
                'from': from_destination,
                'type': bus_type,
                'date': travel_date
            }
            buses.append(bus)


        return render_template("dashboard.html", user=user, show_details_form=True,
                               from_destination=from_destination, to_destination=to_destination,
                               travel_date=travel_date, buses=buses, VALID_DESTINATIONS=VALID_DESTINATIONS)

    return render_template("dashboard.html", user=user, show_details_form=False, VALID_DESTINATIONS=VALID_DESTINATIONS)



@app.route('/passenger_info', methods=['POST'])
@login_required
def passenger_info():
    # Get bus details from the form submission
    print(request.form)
    bus_id = request.form.get('bus_id')
    departure_time = request.form.get('departure_time')
    a_time = request.form.get('arrival_time')
    date = request.form.get('date')
    from_city = request.form.get('from')
    to_city = request.form.get('to')
    price = request.form.get('price')
    user = request.form.get('user')
    bus_type = request.form.get('bus_type')
    string_atime = a_time
    sp = int(price.replace('₹', '').replace(',', '').strip())
    seat_price = sp
# Convert the string to a list
    arrival_time = ast.literal_eval(string_atime)


    # Render the passenger info page with bus details
    return render_template('passenger_info.html', user=user, bus_id=bus_id, departure_time=departure_time,
                           arrival_time=arrival_time, date=date, from_city=from_city, to_city=to_city, price=price,seat_price=seat_price,bus_type=bus_type)

@app.route('/ticket_confirmation', methods=['POST'])
@login_required
def ticket_confirmation():
    # Get all the details from the form submission
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    address = request.form.get('address')
    country = request.form.get('country')
    state = request.form.get('state')
    zip = request.form.get('zip')
    total_price = request.form.get('total_price')
    bus_type = request.form.get('bus_type')
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    departure_time = request.form.get('departure_time')
    arrival_time = request.form.get('arrival_time')
    date = request.form.get('date')
    seat_count = request.form.get('seat_count')
    # Here, you can process the booking (e.g., save to the database, send email confirmation, etc.)

    # Render the ticket confirmation page
    return render_template('ticket_confirmation.html', first_name=first_name, last_name=last_name,
                           email=email, address=address, country=country, state=state,
                           zip_code=zip, total_price=total_price, bus_type=bus_type,
                           from_city=from_city, to_city=to_city,
                           departure_time=departure_time, arrival_time=arrival_time, date=date,seat_count=seat_count)



@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please Login First.', 'warning')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
