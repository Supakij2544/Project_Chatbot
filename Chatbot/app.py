# ไฟล์นี้จะทำงานฝั่ง server เวลา user ยิงคำขอมาไฟล์นี้ก็จะตอบกลับไปในรูปแบบ json
# เวลาเดิมในคลิบ 1:16:50
from flask import Flask 
from flask_restful import Api,Resource,abort,marshal_with,fields,reqparse #สร้าง API และ Resource และ abort คือตัวกำหนดข้อความที่เราต้องการให้ตอบกลับไป
from flask_sqlalchemy import SQLAlchemy,Model
app = Flask(__name__)

################################################
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
        record = RecordModel(User_ID=User_ID,Trip_name=args["Trip_name"],Hotel_name=args["Hotel_name"]) #####
        db.session.add(record) #####
        db.session.commit() # เปลี่ยนแปลงข้อมูลในฐานข้อมูล #####
        return record,201 # 201 คือการเพิ่มข้อมูลลงฐานข้อมูล #####
        # return args

# Call     
api.add_resource(Record,"/record/<string:User_ID>")


################################################
if __name__ == "__main__":
    app.run(debug=True)


