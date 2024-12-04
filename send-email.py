from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth
from flask_mail import Mail, Message

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'random_secret_key'

# OAuth setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='YOUR_GOOGLE_CLIENT_ID',  # Replace with your actual Google client ID
    consumer_secret='YOUR_GOOGLE_CLIENT_SECRET',  # Replace with your actual Google client secret
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

# Setup for Flask-Mail (optional for sending email from Flask)
mail = Mail(app)

# Google OAuth login route
@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

# OAuth callback route
@app.route('/login/callback')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(request.args['error_reason'], request.args['error_description'])
    
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    session['user_email'] = user_info.data['email']
    return redirect(url_for('report_problem'))

# Report Problem route
@app.route('/report-problem', methods=['GET', 'POST'])
def report_problem():
    if request.method == 'POST':
        # If the user is not logged in, redirect them to login with Google
        if 'google_token' not in session:
            return redirect(url_for('login'))

        # Get form data
        fname = request.form['fname']
        lname = request.form['lname']
        message = request.form['message']

        # Get user's email from the session
        user_email = session.get('user_email')

        # Send email via Gmail
        msg = Message(
            subject=f"Problem reported by {fname} {lname}",
            sender=user_email,
            recipients=["zsaiyed138@gmail.com"],  # Add recipient email
            body=message
        )
        mail.send(msg)

        return "Email Sent Successfully!"

    # If GET request, render the form
    return '''
        <form action="/report-problem" method="POST">
            <label for="fname">First Name:</label>
            <input type="text" id="fname" name="fname" required><br>

            <label for="lname">Last Name:</label>
            <input type="text" id="lname" name="lname" required><br>

            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required><br>

            <label for="message">Message:</label>
            <textarea id="message" name="message" required></textarea><br>

            <button type="submit">Submit</button>
            <button type="reset">Clear Form</button>
        </form>
    '''

# OAuth token getter
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

if __name__ == '__main__':
    app.run(debug=True)
