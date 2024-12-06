from flask import Flask, render_template, redirect, request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from unit16_converters import floatToUint16, floatConvertion
from ModbusTCPClient import Modbus
from datetime import datetime


# My App Setup
app = Flask(__name__)
Scss(app)

ModbusHost = 'localhost'
Modbusport = 1562
unitID = 1

modbusClient = Modbus(ModbusHost,Modbusport,unitID)
connection = modbusClient.modbusConnect()    

#Home Page
@app.route('/')
def home():
    return render_template('homepage.html')

#items go in order of the Homepage


@app.route('/activities')
def activties():
    return render_template('activities.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/contact')
def contact():
    return render_template('contactinfo.html')

@app.route('/rotary')
def rotary():
    return render_template('rotary.html')
    
@app.route('/report')
def report():
    return render_template('index.html')


#Everything In the Ssa directory
@app.route('/ssa')
def ssa():
    return render_template('SSA.html')

@app.route('/ssa/weather')
def weather():
    return render_template('weather.html')

@app.route('/ssa/temperature-adjustment',methods=['POST', 'GET'])
def temperature_adjustment():
    IR = modbusClient.modbusRead('ir',0,6)
    HR = modbusClient.modbusRead('hr',0,4)
    SetTemp = floatConvertion(HR[0], HR[1])
    SetHimid = floatConvertion(HR[2], HR[3]) 
    roomTemp = floatConvertion(IR[0], IR[1])
    roomHimid = floatConvertion(IR[4], IR[5])
    return render_template('index.html',roomTemp=roomTemp, roomHimid=roomHimid, SetTemp=SetTemp, SetHimid=SetHimid)

@app.route('/submit',methods=['POST'])
def submit():
    if request.method == 'POST':
        InputTemp = request.form['InputTemp']
        InputHimid = request.form['InputHimid']
        
        ST_Unit16 = floatToUint16(float(InputTemp))
        SH_Uint16 = floatToUint16(float(InputHimid))
        modbusClient.modbusWrite('hr',0,ST_Unit16, True)
        modbusClient.modbusWrite('hr',2,SH_Uint16, True)
        return redirect('/temperature-adjustment')
    

    
app = Flask(__name__)

@app.route('/send-email', methods=['GET', 'POST'])
def send_email():
    print(f"Request Method: {request.method}")
    if request.method == 'POST':
        # Get subject and message from the form
        subject = request.form['subject']
        message = request.form['message']
       
        # Hard-code the recipient's email
        recipient = 'zsaiyed@gmail.com'  # Replace with the desired recipient email

        # Create the mailto link with the subject and body
        mailto_link = f"mailto:{recipient}?subject={subject}&body={message}"

        # Redirect the user to their email client (Gmail in this case)
        return redirect(mailto_link)

    return render_template('index.html')





# Runner and Dubgger
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)