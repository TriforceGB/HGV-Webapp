from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit 
from flask_mail import Mail, Message 
import smtplib
import websocket
import threading
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

websocket_data = None

def on_message(ws, message):
    global websocket_data
    websocket_data=message
    print("Received from websocket: ", message)
    socketio.emit('new_data', {'data': message})

def on_error(ws, error):
    print("Error: ", error)

def on_close(ws, close_status_code, close_msg):
    print("Closed websocket connection")

def on_open(ws):
    print("Websocket connection established")

def start_websocket():
    ws_url=  "ws://192.168.3.126:1880/ws/temp"
    print(f"Connecting to websocket at {ws_url}")
    ws = websocket.WebSocketApp(ws_url,
                                on_message = on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def run_websocket_thread():
    websocket_thread =threading.Thread(target=start_websocket)
    websocket_thread.daemon=True
    websocket_thread.start()

def send_email_to_osticket(user_email, subject, message):
    from_email = os.getenv("FROM_EMAIL")
    from_password = os.getenv("FROM_PASSWORD")

    to_email = "support@hgvsupport.ddns.net"

    email_message = MIMEMultipart()
    email_message['From'] = user_email
    email_message['To'] = to_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)


        server.starttls()
        server.login(from_email, from_password)

        text = email_message.as_string()
        result = server.sendmail(from_email, to_email, text)

        if not result:
            print("Email sent to osTicket!!")
        else:
            print(f"Failed to send email to: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()


@app.route('/ssa/temperature-adjustment')
def temperature_adjustment():
    global websocket_data
    roomTemp= websocket_data if websocket_data else 22
    SetTemp = roomTemp

    return render_template("temp.html", roomTemp=roomTemp, SetTemp=SetTemp)

@socketio.on('request_data') 
def handle_request_data():
    global websocket_data
    if websocket_data:
        emit('new_data', {'data': websocket_data})

#Home Page
@app.route('/')
def home():
    return render_template('homepage.html')

#items go in order of the Homepage


@app.route('/activities')
def activities():
    return render_template('activities.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/contact')
def contact():
    return render_template('contactInfo.html')

@app.route('/rotary')
def rotary():
    return render_template('rotary.html')
    
@app.route('/report')
def report():
    return render_template('reportprob.html')

#Everything In the Ssa directory
@app.route('/ssa')
def ssa():
    return render_template('SSA.html')

@app.route('/ssa/weather')
def weather():
    return render_template('weather.html')

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/send-email', methods=['GET', 'POST'])
def send_email():
    if request.method == 'POST':
        try:
            user_email = request.form['email']
        # Get subject and message from the form
            subject = request.form['subject']
            message = request.form['message']
       
            send_email_to_osticket(user_email, subject, message)
            return render_template('reportprob.html', message="Email sent!!")
        

        except Exception as e:
            return render_template('reportprob.html', message=f"Error sending email: {str(e)}")
    return render_template('reportprob.html')


# Runner and Dubugger
if __name__ == '__main__':
    run_websocket_thread()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
