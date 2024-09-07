from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for session management

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized access


# User class to store user information
class User(UserMixin):
    def __init__(self, id, name, username, email):
        self.id = id
        self.name = name
        self.username = username
        self.email = email

    # Flask-Login requires a user loader function


@login_manager.user_loader
def load_user(user_id):
    # Load the user data from CSV based on user ID (index in the CSV)
    content = pd.read_csv("userdata.csv")
    user_row = content.loc[int(user_id)]

    if user_row is not None:
        return User(id=user_id, name=user_row['name'], username=user_row['username'], email=user_row['email'])
    return None


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

            # Load existing user data
            content = pd.read_csv("userdata.csv")
            x = content.username.to_list()
            y = content.email.to_list()

            # Check if the username or email already exists
            if username in x or email in y:
                return '<h1>Username or email already exists. Please try a different one.</h1>'
            else:
                # Add the new user to the dataframe
                new_user = pd.DataFrame({
                    'name': [name],
                    'username': [username],
                    'email': [email],
                    'password': [password]
                })

                # Append the new user data to the CSV
                content = content._append(new_user, ignore_index=True)
                content.to_csv("userdata.csv", index=False)

                # Redirect to the dashboard route with the username parameter
                return redirect(url_for('dashboard', user=name))

        elif 'username' in request.form:
            input_data = request.form['username']  # This could be either username or email
            password = request.form['password']

            # Load user data from CSV
            content = pd.read_csv("userdata.csv")
            usernames = content['username'].to_list()
            emails = content['email'].to_list()

            # Determine if input is username or email
            if input_data in usernames:
                user_row = content[content['username'] == input_data]
            elif input_data in emails:
                user_row = content[content['email'] == input_data]
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return redirect(url_for('login'))

            # Get the password and name from the user row
            user_password = user_row['password'].values[0]
            user_name = user_row['name'].values[0]
            user_id = user_row.index[0]  # Use the index as the user ID

            # Simple user authentication check
            if user_password == password:
                user = User(id=user_id, name=user_name, username=input_data, email=user_row['email'].values[0])
                login_user(user)  # Log the user in
                # Redirect to the dashboard route with the user's name
                return redirect(url_for('dashboard', user=user_name))
            else:
                flash('Invalid credentials, please try again.', 'danger')
                return redirect(url_for('login'))

    return render_template('sign-up.html')


@app.route('/dashboard/<user>')
@login_required
def dashboard(user):
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
    app.run(debug=True)
