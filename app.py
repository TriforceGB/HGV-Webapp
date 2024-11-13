from flask import Flask, render_template, redirect, request
from flask_socketio import SocketIO, emit
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from unit16_converters import floatToUint16, floatConvertion
from ModbusTCPClient import Modbus
from datetime import datetime

# My App Setup
app = Flask(__name__)
Scss(app)
Socketio = SocketIO(app)

#SQL Alchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///HGV_DB.db" # Changed to Real Dir Later
db = SQLAlchemy(app)

class SensorData(db.Model):
    __tablename__ = 'Sensors'
    time = db.Column('time', db.DateTime, primary_key=True)
    temperature_DHT22 = db.Column('temperature_DHT22', db.Float)
    temperature_DS18B20 = db.Column('temperature_DS18B20', db.Float)
    humidity_DHT22 = db.Column('humidity_DHT22', db.Float)
    motion = db.Column('motion', db.Boolean)
    smoke = db.Column('smoke', db.Boolean)
    waterLeak = db.Column('waterLeak', db.Boolean)
    vibration = db.Column('vibration', db.Boolean)
    setTemperature = db.Column('SetTemperature', db.Float)
    setHumidity = db.Column('SetHumidity', db.Float)
#Starting up Modbus
ModbusHost = 'localhost'
Modbusport = 1562
unitID = 1

modbusClient = Modbus(ModbusHost,Modbusport,unitID)
connection = modbusClient.modbusConnect()    
#Home Page
@app.route('/',methods=['POST', 'GET'])
def index():
    IR = modbusClient.modbusRead('ir',0,6)
    HR = modbusClient.modbusRead('hr',0,4)
    SetTemp = floatConvertion(HR[0], HR[1])
    SetHimid = floatConvertion(HR[2], HR[3]) 
    roomTemp = floatConvertion(IR[0], IR[1])
    roomHimid = floatConvertion(IR[4], IR[5])
    return render_template('index.html',roomTemp=roomTemp, roomHimid=roomHimid, SetTemp=SetTemp, SetHimid=SetHimid)

@app.route('/test')
def test():
    latest_entry = SensorData.query.order_by(SensorData.time.desc()).first()

    return str(latest_entry.humidity_DHT22)


@Socketio.on('NewData')
def NewData():
    CurrentEntry = SensorData.query.order_by(SensorData.time.desc()).first()
    CurrentTemp = str(CurrentEntry.temperature_DHT22)
    CurrentHimid = str(CurrentEntry.humidity_DHT22)
    
    emit('CurrentRoomData', {'CurrentTemp':CurrentTemp, 'CurrentHimid':CurrentHimid}, broadcast=True)
    
    
@Socketio.on('connect')
def handle_connect():
    print("Client connected")  # Debugging log
    ocketio.start_background_task(monitor_database)
    
    

#Handels when user changes Wanted Tempasure and Himdity
@app.route('/submit',methods=['POST'])
def submit():
    if request.method == 'POST':
        InputTemp = request.form['InputTemp']
        InputHimid = request.form['InputHimid']
        
        ST_Unit16 = floatToUint16(float(InputTemp))
        SH_Uint16 = floatToUint16(float(InputHimid))
        modbusClient.modbusWrite('hr',0,ST_Unit16, True)
        modbusClient.modbusWrite('hr',2,SH_Uint16, True)
        return redirect('/')


# Runner and Dubgger
if __name__ == '__main__':
    Socketio.run(app),