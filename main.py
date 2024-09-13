from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

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
    'from': ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Pune",
             "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
             "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Chandigarh", "Coimbatore",
             "Kochi", "Guwahati", "Amritsar", "Jodhpur", "Agra"],
    'to': ["Delhi", "Mumbai", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Pune",
           "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore",
           "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Chandigarh", "Coimbatore",
           "Kochi", "Guwahati", "Amritsar", "Jodhpur", "Agra"]
}


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

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/test')
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

@app.route('/dashboard/<user>', methods=['GET', 'POST'])
@login_required
def dashboard(user):
    if request.method == 'POST':
        from_destination = request.form.get('from-destination').title()
        to_destination = request.form.get('to-destination').title()

        if from_destination not in VALID_DESTINATIONS['from']:
            flash('Please select a valid city from the "From" dropdown menu.', 'danger')
            return redirect(url_for('dashboard', user=user))

        if to_destination not in VALID_DESTINATIONS['to']:
            flash('Please select a valid city from the "To" dropdown menu.', 'danger')
            return redirect(url_for('dashboard', user=user))

        if to_destination == from_destination:
            flash('Please select a different city.', 'danger')
            return redirect(url_for('dashboard', user=user))

        # Proceed with further processing (e.g., searching for buses)
        return "Search submitted successfully"

    return render_template("dashboard.html", user=user)

@app.route('/contact_us')
def contact_page():
    return render_template('contact_page.html')

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
