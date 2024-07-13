from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# authentication
users = {
    'testuser': 'password123'
}


@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simple user authentication check
        if username in users and users[username] == password:
            return redirect(url_for('dashboard'))
        else:
            return '<h1>Invalid credentials, please try again.</h1>'

    return render_template('sign-in.html')


@app.route('/dashboard')
def dashboard():
    return 'Welcome to your dashboard!'


if __name__ == '__main__':
    app.run(debug=True)
