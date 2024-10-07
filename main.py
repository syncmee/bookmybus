from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib, random
from flask import Flask, redirect, url_for, session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests, ast, gunicorn
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta
import pdfcrowd
import sys
import os
import tempfile
import psycopg2
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# Email-Setup
mail = os.getenv("EMAIL")
mail_password = os.getenv("EMAIL_PASSWORD")

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized access

today_date = datetime.now()
booking_day = today_date.strftime('%a, %d %B %Y')

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
api_key = os.getenv("MAPBOX_API_KEY")

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


# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid email profile'},
)

github = oauth.register(
    name='github',
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    userinfo_endpoint='https://api.github.com/user',
    client_kwargs={'scope': 'user:email'},
)

facebook = oauth.register(
    name='facebook',
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://www.facebook.com/dialog/oauth',
    authorize_params=None,
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email public_profile'}
)


# User model for SQLAlchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)  # Make password optional for Google logins
    google_id = db.Column(db.String(100), unique=True, nullable=True) # Google ID for OAuth
    github_id = db.Column(db.String(100), unique=True, nullable=True) # GitHub ID for OAuth
    facebook_id = db.Column(db.String(100), unique=True, nullable=True) # Facebook ID for OAuth

class TicketBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key linking to the User table
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pnr = db.Column(db.String(20), nullable=False)
    bus_type = db.Column(db.String(50), nullable=False)
    from_city = db.Column(db.String(100), nullable=False)
    to_city = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.String, nullable=False)
    arrival_time = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    selected_seats = db.Column(db.String, nullable=False)
    selected_seat_count = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String, nullable=False)
    booking_date = db.Column(db.DateTime, default=booking_day, nullable=False)

    # Relationship to link back to User
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))

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

        # Email configuration
        receiver_email = email
        sender_email = 'bookmybus.info@gmail.com'
        password = 'qprp xuxk gaml bdca'
        email_subject = f"{name} [Subject - {subject}] - bookmybus"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Create the MIMEMultipart object
        message = MIMEMultipart("alternative")
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = email_subject

        # Read the HTML content from an external file
        html_file_path = "templates/contact_us.html"  # Path to  HTML file

        with open(html_file_path, "r") as file:
            html_content = file.read()


        # Attach the HTML content to the email
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Sending the email
        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Upgrade the connection to a secure encrypted TLS connection

            # Login to the email account
            server.login(sender_email, password)

            # Send the email
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")

        finally:
            # Close the connection
            server.quit()

    return render_template('homepage.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')
@app.route('/terms')
def test():
    return render_template('test.html')

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

@app.route('/google')
def google_login():
    redirect_uri = url_for('auth_callback', _external=True,_scheme='https')
    print(f'Redirect URI: {redirect_uri}')  # Check if this matches the one in Google Console
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    # Get the token and user info
    token = google.authorize_access_token()
    user_info = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()

    # Extract user info
    user_email = user_info['email']  # Get the email from Google user info
    user_name = user_email.split('@')[0]  # Extract username from email
    name = user_info.get('name', '')  # Get the user's name
    google_id = user_info['sub']  # Google ID

    # Check if user exists in your database by email
    user = User.query.filter_by(email=user_email).first()

    if user:
        # If the user exists, log them in
        login_user(user)  # Use Flask-Login to manage the session
        session['email'] = user.email

        # Check if Google ID is already linked; if not, link it
        if not user.google_id:
            user.google_id = google_id  # Link the Google account
            db.session.commit()  # Commit the changes to the database

    else:
        # User does not exist, create a new account
        new_user = User(email=user_email, name=name, google_id=google_id, username=user_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)  # Log the new user in
        session['email'] = user_email

    return redirect(url_for('dashboard', user=current_user.name))  # Render the dashboard with the user's name

@app.route('/login/github')
def github_login():
    redirect_uri = url_for('github_callback', _external=True,_scheme='https')
    return github.authorize_redirect(redirect_uri)

@app.route('/github/callback')
def github_callback():
    # Get the token and user info from GitHub
    token = github.authorize_access_token()
    profile_resp = github.get('https://api.github.com/user')
    profile = profile_resp.json()

    # Get the user's email from the separate GitHub API call
    emails_resp = github.get('https://api.github.com/user/emails')
    emails = emails_resp.json()

    # Find the primary, verified email
    primary_email = None
    for email in emails:
        if email['primary'] and email['verified']:
            primary_email = email['email']
            break

    if primary_email is None:
        primary_email = 'No primary verified email found'

    # Extract GitHub-specific info
    username = profile['login']
    name = profile.get('name', '')  # Get the GitHub user's name, default to an empty string if unavailable
    github_id = profile['id']  # GitHub ID

    # Check if the user exists in your database by email
    user = User.query.filter_by(email=primary_email).first()

    if user:
        # If the user exists, log them in
        login_user(user)  # Use Flask-Login to manage the session
        session['email'] = user.email

        # Check if GitHub ID is already linked; if not, link it
        if not user.github_id:
            user.github_id = github_id  # Link the GitHub account
            db.session.commit()  # Commit the changes to the database
    else:
        # User does not exist, create a new account
        new_user = User(email=primary_email, name=name, github_id=github_id, username=username)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)  # Log the new user in
        session['email'] = primary_email

    return redirect(url_for('dashboard', user=current_user.name))  # Redirect to the dashboard with the user's name

@app.route('/login/facebook')
def facebook_login():
    redirect_uri = url_for('auth_facebook', _external=True,_scheme='https')
    return oauth.facebook.authorize_redirect(redirect_uri)

@app.route('/auth/facebook/callback')
def auth_facebook():
    # Get the token and user info from Facebook
    token = facebook.authorize_access_token()
    user_info = facebook.get('https://graph.facebook.com/me?fields=id,name,email').json()

    # Extract user info
    user_email = user_info['email']  # Get the email from Facebook user info
    user_name = user_email.split('@')[0]  # Extract username from email
    name = user_info.get('name', '')  # Get the user's name
    facebook_id = user_info['id']  # Facebook ID

    # Check if user exists in your database by email
    user = User.query.filter_by(email=user_email).first()

    if user:
        # If the user exists, log them in
        login_user(user)  # Use Flask-Login to manage the session
        session['email'] = user.email

        # If Facebook ID is not already linked, link it
        if not user.facebook_id:
            user.facebook_id = facebook_id  # Link the Facebook account
            db.session.commit()  # Commit the changes to the database

    else:
        # User does not exist, create a new account
        new_user = User(email=user_email, name=name, facebook_id=facebook_id, username=user_name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)  # Log the new user in
        session['email'] = user_email

    # Redirect to dashboard with the user's name
    return redirect(url_for('dashboard', user=current_user.name))

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
    flash('Please Choose Your Seats', 'danger')
    # Here, you can process the booking (e.g., save to the database, send email confirmation, etc.)


    # Render the passenger info page with bus details
    return render_template('passenger_info.html', user=user, bus_id=bus_id, departure_time=departure_time,
                           arrival_time=arrival_time, date=date, from_city=from_city, to_city=to_city, price=price,seat_price=seat_price,bus_type=bus_type)

@app.route('/ticket_confirmation', methods=['POST'])
@login_required
def ticket_confirmation():
    flash('Your ticket is booked for this journey!', 'success')
    # Get all the details from the form submission
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    address = request.form.get('address')
    country = request.form.get('country')
    state = request.form.get('state')
    zip = request.form.get('zip')
    bus_type = request.form.get('bus_type')
    from_city = request.form.get('from_city')
    to_city = request.form.get('to_city')
    departure_time = request.form.get('departure_time')
    arrival_time = request.form.get('arrival_time')
    date = request.form.get('date')
    selected_seats = request.form.get('selected_seats')
    selected_seat_count = request.form.get('selected_seat_count')
    age = request.form.get('age')
    digit_4 = random.choice(range(1000, 9999))
    total_price = request.form.get('total_price')
    duration = request.form.get('duration')
    pnr = f"BMB{digit_4}"

    # Check if a booking already exists for this user with the same details
    existing_booking = TicketBooking.query.filter_by(
        user_id=current_user.id,
        from_city=from_city,
        to_city=to_city,
        departure_time=departure_time,
        date=date
    ).first()

    if existing_booking:
        flash('You have already booked a ticket for this journey!', 'warning')
        return redirect(url_for('bookings', user=current_user.name))

    # Create a new TicketBooking record
    new_booking = TicketBooking(
        user_id=current_user.id,  # Reference to the current logged-in user
        first_name=first_name,
        last_name=last_name,
        email=email,
        address=address,
        country=country,
        state=state,
        pnr=pnr,
        bus_type=bus_type,
        from_city=from_city,
        to_city=to_city,
        departure_time=departure_time,
        arrival_time=arrival_time,
        date=date,
        age=age,
        selected_seats=selected_seats,
        selected_seat_count=selected_seat_count,
        total_price=total_price,
        duration=duration

    )

    db.session.add(new_booking)
    db.session.commit()

    # Email configuration
    receiver_email = email
    sender_email = 'bookmybus.info@gmail.com'
    password = 'qprp xuxk gaml bdca'
    email_subject = "Ticket Confirmation- bookmybus"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the MIMEMultipart object
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = email_subject

    # Read the HTML content from an external file
    html_file_path = "templates/ticket_booked.html"  # Path to  HTML file

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_file = file.read()
        html_content = html_file.replace('[TotalPrice]', total_price).replace('[DATE]',booking_day).replace('[NAME]', first_name.title() +' '+ last_name.title()).replace('[BMB####]', pnr).replace('[FROM]',from_city).replace('[TO]',to_city).replace('[BUSTYPE]', bus_type).replace('[DEP-DATE]',date).replace('[SEAT-NO]', selected_seats).replace('[DEP-TIME]',departure_time).replace('[ARV-TIME]',arrival_time)

    # Attach the HTML content to the email
    html_part = MIMEText(html_content, "html", "utf-8")
    message.attach(html_part)

    # Sending the email
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to a secure encrypted TLS connection

        # Login to the email account
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

    finally:
        # Close the connection
        server.quit()


    # Render the ticket confirmation page
    return render_template('ticket_confirmation.html', first_name=first_name, last_name=last_name,
                           email=email, address=address, country=country, state=state,
                           zip_code=zip, bus_type=bus_type,
                           from_city=from_city, to_city=to_city,
                           departure_time=departure_time, arrival_time=arrival_time, date=date,selected_seats=selected_seats,selected_seat_count=selected_seat_count,age=age,pnr=pnr,total_price=total_price,duration=duration)

@app.route('/dashboard/bookings')
@login_required
def bookings():
    user_bookings = current_user.bookings  # Get all bookings for the logged-in user
    current_time = datetime.now()
    for booking in user_bookings:
        booking.date_formated = datetime.strptime(booking.date, '%B %d, %Y')
    return render_template('bookings.html', bookings=user_bookings, current_time=current_time)


@app.route('/dashboard/cancel')
@login_required
def cancellation():
    user_bookings = current_user.bookings  # Get all bookings for the logged-in user
    current_time = datetime.now()
    for booking in user_bookings:
        booking.date_formated = datetime.strptime(booking.date, '%B %d, %Y')
    return render_template('cancellation.html', bookings=user_bookings, current_time=current_time)

@app.route('/dashboard/status')
@login_required
def status():
    user_bookings = current_user.bookings  # Get all bookings for the logged-in user
    current_time = datetime.now()
    for booking in user_bookings:
        booking.date_formated = datetime.strptime(booking.date, '%B %d, %Y')
    return render_template('status.html', bookings=user_bookings, current_time=current_time)


@app.route('/remove_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def remove_ticket(ticket_id):
    ticket = TicketBooking.query.get_or_404(ticket_id)
    # Ensure that the current user is authorized to delete the ticket
    if ticket.user_id != current_user.id:
        flash("You are not authorized to remove this ticket", 'danger')
        return redirect(url_for('bookings', user=current_user.name))

    db.session.delete(ticket)
    db.session.commit()
    flash("Ticket has been removed successfully!", 'success')
    return redirect(url_for('bookings', user=current_user.name))

@app.route('/cancel_ticker/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    ticket = TicketBooking.query.get_or_404(ticket_id)
    # Ensure that the current user is authorized to delete the ticket
    if ticket.user_id != current_user.id:
        flash("You are not authorized to remove this ticket", 'danger')
        return redirect(url_for('cancellation', user=current_user.name))

    db.session.delete(ticket)
    db.session.commit()
    flash("Ticket has been cancelled successfully!", 'danger')
    return redirect(url_for('cancellation', user=current_user.name))
@app.route('/download_ticket/<int:ticket_id>')
def download_ticket(ticket_id):
    # Fetch the booking details from the database using ticket_id
    booking = TicketBooking.query.get_or_404(ticket_id)  # Implement this function
    name = f"{booking.first_name} {booking.last_name}"

    try:
        # Create the API client instance
        client = pdfcrowd.HtmlToPdfClient('syncme', '0473b692705df598eb4ee6ec77f82839')

        # Render the HTML directly to a string
        rendered_html = render_template('ticketpdf.html', name=name, pnr=booking.pnr,
                                        FROM_CITY=booking.from_city, to_city=booking.to_city, dep=booking.departure_time, arv=booking.arrival_time,
                                        duration=booking.duration, seats=booking.selected_seats, date=booking.date,
                                        bustype=booking.bus_type,age=booking.age)

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as temp_html:
            temp_html.write(rendered_html.encode('utf-8'))
            temp_html_path = temp_html.name

        # Define the output PDF file path
        output_file_path = os.path.join(app.root_path, 'static', f'{booking.pnr}-Ticket.pdf')

        # Run the conversion using the temporary HTML file
        client.convertFileToFile(temp_html_path, output_file_path)

        # Send the generated PDF file to the user
        return send_file(output_file_path, as_attachment=True)

    except pdfcrowd.Error as why:
        sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
        return "An error occurred while generating the PDF: {}".format(why), 500

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)



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