from flask import Flask, render_template, request, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd

app = Flask(__name__)

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
                    'name' : [name],
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
                return '<h1>Invalid credentials, please try again.</h1>'

            # Get the password and name from the user row
            user_password = user_row['password'].values[0]
            user_name = user_row['name'].values[0]

            # Simple user authentication check
            if user_password == password:
                # Redirect to the dashboard route with the user's name
                return redirect(url_for('dashboard', user=user_name))
            else:
                return '<h1>Invalid credentials, please try again.</h1>'

    return render_template('sign-up.html')


@app.route('/dashboard/<user>')
def dashboard(user):
    return render_template("dashboard.html", user=user)

@app.route('/contact_us')
def contact_page():
    return render_template('contact_page.html')




if __name__ == '__main__':
    app.run(debug=True)
