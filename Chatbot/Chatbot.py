#Chatbot Tutorial with Firebase
#Import Library
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from function_chatbot import *
from flask_restful import Api,Resource,abort,marshal_with,fields,reqparse #สร้าง API และ Resource และ abort คือตัวกำหนดข้อความที่เราต้องการให้ตอบกลับไป
from flask_sqlalchemy import SQLAlchemy,Model
from SQLite_RoarDatabase import Query # SQLite database

#---- Google Sheet ----
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
cerds = ServiceAccountCredentials.from_json_keyfile_name("cerds.json", scope)
client = gspread.authorize(cerds)
sheet1 = client.open("Chatbot_notify").worksheet('Sheet1')
sheet2 = client.open("Chatbot_notify").worksheet('Sheet2')
#-------------------------------------

# ---------- SQLite database ----------
# # Difine connection and cursor
# connection = sqlite3.connect('database.db') # Connect python with SQLite
# cursor = connection.cursor()
# ---------- SQLite database ----------

# Flask
app = Flask(__name__)

####################### Save data #######################

# Database
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
api = Api(app)

# คลาสนี้เชื่อมต่อกับฐานข้อมูล (SQLite) ถ้าข้อมูลในนี้เปลี่ยนในตารางของฐานข้อมูลก็จะเปลี่ยน
class RecordModel(db.Model):
    User_ID = db.Column(db.String,primary_key=True)
    Trip_name = db.Column(db.String(500),nullable=False)
    Hotel_name = db.Column(db.String(500),nullable=False)

    def __repr__(self):
        return f"Record(Trip_name={Trip_name},Hotel_name={Hotel_name})"

db.create_all()

# Request reqparse
record_add_args = reqparse.RequestParser()
record_add_args.add_argument("Trip_name",type=str,required=True,help="กรุณาป้อนชื่อทริปเป็นตัวอักษรหรือระบุชื่อทริปด้วยครับ") # help จะส่งการแจ้งเตือนกลับในกรณีที่เราระบุ argument ไม่ตรง type
record_add_args.add_argument("Hotel_name",type=str,required=True,help="กรุณาป้อนชื่อโรงแรมเป็นตัวอักษรหรือระบุชื่อโรงแรมด้วยครับ")

record = {
    "1":{"Trip":"วัดพระแก้ว","Hotel":"โรงแรม A"}, 
    "2":{"Trip":"เกาะล้าน","Hotel":"โรงแรม B"},
    "3":{"Trip":"สวนสยาม","Hotel":"โรงแรม C"},
}

# Record data in to Database
resource_field = {
    "User_ID":fields.String,
    "Trip_name":fields.String,
    "Hotel_name":fields.String
}

# validate request
def notFoundID(User_ID):
    if User_ID not in record:
        abort(404,message = "ไม่พบข้อมูลที่คุณร้องขอ")
# def notFoundTripName(Trip_name):
#     if Trip_name not in record:
#         abort(404,message="ไม่พบชื่อทริปที่คุณร้องขอ")

# Design
class Record(Resource):
    @marshal_with(resource_field)
    def get(self,User_ID): # ขอข้อมูล #####
        notFoundID(User_ID)
        return record[User_ID] # {"key","value"}

    @marshal_with(resource_field) #####
    def post(self,User_ID): # สร้างข้อมูล
        args = record_add_args.parse_args()
        record = RecordModel(User_ID=User_ID,Trip_name=args["Trip_name"],Hotel_name=args["Hotel_name"]) ##### บันทึก
        db.session.add(record) #####
        db.session.commit() # เปลี่ยนแปลงข้อมูลในฐานข้อมูล #####
        return record,201 # 201 คือการเพิ่มข้อมูลลงฐานข้อมูล #####
        # return args

# Call     
api.add_resource(Record,"/record/<string:User_ID>")

####################### Save data #######################

@app.route('/', methods=['POST']) #Using post as a method

def MainFunction():

    #Getting intent from Dailogflow
    question_from_dailogflow_raw = request.get_json(silent=True, force=True)
    if question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'place_request':
        answer_from_bot = place_request(question_from_dailogflow_raw)
    elif question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'place_recommendation':
        answer_from_bot = place_recommendation(question_from_dailogflow_raw)
    elif question_from_dailogflow_raw["queryResult"]["intent"]["displayName"] == 'trip_recommendation':
        answer_from_bot = trip_recommendation(question_from_dailogflow_raw)
    else:
        #Call generating_answer function to classify the question
        answer_from_bot = generating_answer(question_from_dailogflow_raw)
    #Make a respond back to Dailogflow
    r = make_response(answer_from_bot)
    r.headers['Content-Type'] = 'application/json' #Setting Content Type
    return r


def generating_answer(question_from_dailogflow_dict):

    #Print intent that recived from dialogflow.
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))

    #Getting intent name form intent that recived from dialogflow.
    intent_group_question_str = question_from_dailogflow_dict["queryResult"]["intent"]["displayName"]

    #Select function for answering question
    if intent_group_question_str == 'หิวจัง':
        answer_str = menu_recormentation()
    elif intent_group_question_str == 'คำนวนน้ำหนัก':
        answer_str = BMI_calculation(question_from_dailogflow_dict)
    elif intent_group_question_str == 'info_schedule':
        answer_str = info_schedule(question_from_dailogflow_dict)
    elif intent_group_question_str == 'save_schedule - yes':
        answer_str = save_schedule(question_from_dailogflow_dict)
        
    elif intent_group_question_str == 'info_trip_hotel': 
        answer_str = info_trip_hotel(question_from_dailogflow_dict)
    elif intent_group_question_str == 'save_trip_hotel - yes': 
        answer_str = save_trip_hotel(question_from_dailogflow_dict)

    #### Query data from SQLite ####
    elif intent_group_question_str == 'request_data':
        answer_str = request_data(question_from_dailogflow_dict)
    #### Query data from SQLite ####
    else: answer_str = "ขอโทษนะคะ ไม่เข้าใจ คุณต้องการอะไร"

    #Build answer dict
    answer_from_bot = {"fulfillmentText": answer_str}

    #Convert dict to JSON
    answer_from_bot = json.dumps(answer_from_bot, indent=4)
    return answer_from_bot


def menu_recormentation(): #ฟังก์ชั่นสำหรับเมนูแนะนำ
    menu_name = 'ข้าวขาหมู'
    answer_function = menu_name + ' สิ น่ากินนะ'
    return answer_function

def BMI_calculation(respond_dict): #Function for calculating BMI

    #Getting Weight and Height
    weight_kg = float(respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Weight.original"])
    height_cm = float(respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Height.original"])

    #Calculating BMI
    BMI = weight_kg/(height_cm/100)**2
    if BMI < 18.5 :
        answer_function = "คุณผอมเกินไปนะ"
    elif 18.5 <= BMI < 23.0:
        answer_function = "คุณมีน้ำหนักปกติ"
    elif 23.0 <= BMI < 25.0:
        answer_function = "คุณมีน้ำหนักเกิน"
    elif 25.0 <= BMI < 30:
        answer_function = "คุณอ้วน"
    else :
        answer_function = "คุณอ้วนมาก"
    return answer_function

def info_schedule(respond_dict):
     time = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["time"][11:16]
     destination = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["destination"]
     date = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["date"][0:10]
     return f'คุณจะไปวันที่ {date} เวลา {time} น. ที่ {destination} ใช่มั้ยคะ?'


def save_schedule(respond_dict):
    time = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["time"][11:16]
    destination = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["destination"]
    date = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["date"][0:10]
    userId = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    sheet1.insert_row([userId,destination,date,time],2)
    return "บันทึกการแจ้งเตือนเรียบร้อยแล้วค่ะ"


def info_trip_hotel(respond_dict): 
    Trip = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Trip"]  
    Hotel = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Hotel"]['business-name']
    return f'คุณจะบันทึกชื่อทริปกับชื่อโรงแรมว่า {Trip} กับ {Hotel} ใช่มั้ยค่ะ?'

def save_trip_hotel(respond_dict): 
    userId = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    Trip = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Trip"]
    Hotel = respond_dict["queryResult"]["outputContexts"][0]["parameters"]["Hotel"]['business-name']
    # record
    URL = f"http://127.0.0.1:5000/record/{userId}"  
    myobj = {'Trip_name':Trip,'Hotel_name':Hotel} 
    x = requests.post(URL, data = myobj)
    # sheet2.insert_row([Trip,Hotel],2)
    return "บันทึกเรียบร้อยแล้วค่ะ"

def request_data(respond_dict):
    User_ID = respond_dict["originalDetectIntentRequest"]["payload"]["data"]["source"]["userId"]
    list_Trip = Query(User_ID)
    if list_Trip == []:
        return "ไม่พบชื่อทริปที่คุณบันทึกเข้ามาค่ะ"
    answer = ""
    for i in list_Trip:
        answer += f"ชื่อทริป : {i[1]} และโรงแรม : {i[2]}\n"
    return answer

#Flask
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)

