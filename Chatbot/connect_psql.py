# psql -U postgres -> คำสั่งในการ login cmd เข้าสู่ PostgreSQL
# insert into record values(parameter1,parameter2,parameter3) -> คำสั่งในการเพิ่มข้อมูลลงในตาราง (postgres)
# \l -> คือคำสั่งในการแสดงฐานข้อมูลทั้งหมด
# \c database_name -> คำสั่งในการเลือกฐานข้อมูลที่จะใช้งาน
# \dt -> คำสั่งแสดงตาราง (table)
import psycopg2 # เป็นไลบารี่ที่ใช้เชื่อมต่อ postgresql กับ python 

#def connect():
con = psycopg2.connect(
    host = 'localhost',
    database = 'chatbot',
    user = 'postgres',
    password = '0634461372'
)
print(con)
cur = con.cursor() # ใช้ฟังก์ชัน cursor ในการคุยกับ database

cur.execute('select * from record;')
print(cur.fetchall())

con.commit()
cur.close()
con.close()

########## note ##########
# ตัวอย่างการ แสดงข้อมูลใน database ผ่าน python
# cur.execute('select * from record;')
# print(cur.fetchall())

# ตัวอย่างการ insert ข้อมูลลง database ผ่าน python
# cur.execute('insert into record values (%s,%s,%s)',('3','Ancient Siam','RoomQuest Sukhumvit 107'))
# print(cur.fetchall())