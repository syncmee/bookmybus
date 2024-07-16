from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)



@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        content = pd.read_csv("userdata.csv")
        x = content.username.to_list()
        user_password = content[content['username'] == username]['password'].values[0]
        # Simple user authentication check
        if username in x and user_password == password:
            # Redirect to the dashboard route with the username parameter
            return redirect(url_for('dashboard', user=username))
        else:
            return '<h1>Invalid credentials, please try again.</h1>'
    return render_template('sign-up.html')

@app.route('/sign-in')
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

    return render_template('sign-up.html')

@app.route('/dashboard/<user>')
def dashboard(user):
    return render_template("dashboard.html", user=user)

@app.route('/contact_us')
def contact_page():
    return render_template('contact_page.html')




if __name__ == '__main__':
    app.run(debug=True)
