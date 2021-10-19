from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from flask_mysqldb import MySQL  # to use db
from flask_mail import Mail, Message
from decouple import config
from datetime import date,datetime

# API_USERNAME = config('USER')
# API_KEY = config('KEY')

#Username: oZiRCgiTkx

#Database name: oZiRCgiTkx

#Password: jDCJtx0I32

Available=100
app = Flask(__name__)
app.config['MYSQL_HOST'] = "remotemysql.com"  # remote.mysql
# if remotemysql give user 📛 *see credentials while creating db
app.config['MYSQL_USER'] = config('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = config(
    'MYSQL_PASSWORD')  # if remotemysql give password🙇
app.config['MYSQL_DB'] = config('MYSQL_DB')  # db name

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template("webpage.html")


@app.route('/form', methods=['POST','GET'])
def form():
    # name, age, address, phno, email, days = "", 0, "", 0, "", 0
    if request.method == 'POST':
        name = request.form["name"]
       # age = request.form["age"]
        address = request.form["address"]
        vaccineName=request.form["vaccineName"]
        dose = request.form["dose"]  # 1 or 2
        phno = request.form["phNo"]
        email = request.form["email"]
        date1 = request.form["date"]
        if(dose == "1"):
            p = (name, vaccineName, address, phno, email)
            cursor = mysql.connection.cursor()
            print("connected to remotemysql")
            cursor.execute(
                    'INSERT INTO consumer(id,name,vaccineName,address,phNo,email) VALUES (NULL,%s,%s,%s,%s,%s)', p)
                
            msg="Thank you for availing the Vaccine. We'll reach you soon via the Mail-id."
        else:
            cursor=mysql.connection.cursor()
            today = date.today()
            date_format = "%Y-%m-%d"
            a = datetime.strptime(date1, date_format)
            b = datetime.strptime(str(today), date_format)
            fro=(b-a).days
            cursor.execute("select Dosage from vaccineDetails where vaccineName='%s'"%vaccineName)
            d=cursor.fetchall()
            for i in d:
                for j in i:
                    if j!="":
                        to=j
            if fro>to:
                p = (name, vaccineName,date1, address, phno, email)
                
                cursor = mysql.connection.cursor()
                print("connected to remotemysql")
                cursor.execute(
                    'INSERT INTO consumer(id,name,vaccineName,dateOfDose1,address,phNo,email) VALUES (NULL,%s,%s,%s,%s,%s,%s)', p)
               
                msg="Thank you for availing the Vaccine. We'll reach you soon via the Mail-id."
            else:
                msg="We are sorry to inform you that You'll need to wait for another "+str(to-int(fro))+" days to avail the second dose of the vaccine."
        mysql.connection.commit()
      
    return render_template("a.html",msg=msg)


@app.route('/login')
def login():
    return render_template("admin.html")


@app.route('/admin', methods=["POST"])
def admin():
    if request.method == 'POST':
        user_id = request.form["userId"]
        password = request.form['password']
        if user_id == "admin" and password == "123":
            return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("admin"))


@app.route('/dashboard')
def dashboard():
    cursor=mysql.connection.cursor()
    cursor.execute('Select vaccineName,stock from vaccineDetails order by vaccineName')
    s=cursor.fetchall()
    Covishield=s[1][1]
    Covaxin=s[0][1]
    cursor.execute(
        "SELECT name,vaccineName,CASE when (dateOfDose1 IS NULL) then 1 else 2 end as dose,email,id FROM consumer where id not in (select id from fullyVaccinated) and id in (select id from consumer where DATEDIFF(CURRENT_DATE,consumer.dateOfDose1) >(select dosage from vaccineDetails where vaccineDetails.vaccineName=consumer.vaccineName )) or id in (select id from consumer where dateOfDose1 is NULL) order by vaccineName,dose")

    count = 0
    mysql.connection.commit()
    Details = cursor.fetchall()
    count=len(Details)
    return render_template("dashboard.html", Details=Details, count=count,Covaxin=Covaxin,Covishield=Covishield)

@app.route("/sendMail",methods=['GET','POST'])
def sendMail():
    if request.method=="POST":
        id=request.form["send"]                               #Get the data from the form(Email)
        cursor=mysql.connection.cursor()
        id=int(id)
        cursor.execute('SELECT email FROM consumer where id=%d'%id)
        a=cursor.fetchall()
        re=a[0][0]
        cursor.execute("SELECT name,vaccineName,CASE when (dateOfDose1 IS NULL) then 1 else 2 end as dose,email FROM consumer where id=%d "%id)
        Details = cursor.fetchall()
        d=[]
        for i in Details:
                for j in i:
                    if j!="":
                        d.append(j)
        sender_mail="balakrishnan1may01@gmail.com"
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'balakrishnan1may01@gmail.com'
        app.config['MAIL_PASSWORD'] = 'Bala2001$'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        mail = Mail(app)                                        # instantiate the mail class
        msg = Message(
            'Vaccination',
            sender=sender_mail,
            recipients=[re]
        )
        msg.body = 'You have been alloted with a slot For getting you vaccinated at XYZ hospital,Coimbatore.'
        #mail.send(msg)                                           #End of code to send Email
        cursor=mysql.connection.cursor()                             #Connect to the server
        today = date.today()
        if d[2]==1:
            cursor.execute("update consumer set dateOfDose1='%s-%s-%s' where id=%d"%(today.year,today.month,today.day,id)) #To add current date as dosage date
            
        else:
            cursor.execute("update consumer set dateOfDose2='%s-%s-%s' where id=%d"%(today.year,today.month,today.day,id)) #To add current date as dosage date
        cursor.execute("update vaccineDetails set stock = stock -1 where vaccineName= '%s'"%(d[1]))
        cursor.execute("insert into fullyVaccinated(id,name,vaccineName,phNo,email) select id,name,vaccineName,phNo,email from consumer where dateOfDose1 is not null and dateOfDose2 is not null and id=%d"%id)
        mysql.connection.commit()  
        
        return redirect(url_for("dashboard"))                        #To redirect to the same page

@app.route('/addStock')
def addStock():
    return render_template("addStock.html")

@app.route('/update',methods=["POST","GET"])
def update():
    if request.method=="POST":
        vaccineName=request.form["vaccineName"]
        amount=request.form["amount"]
        cursor=mysql.connection.cursor()
        cursor.execute("update vaccineDetails set stock=stock+%d where vaccineName='%s'"%(int(amount),vaccineName))
        mysql.connection.commit() 
        return redirect(url_for("dashboard"))

if __name__ == '__main__':
    app.run(debug=True)  # debug true will automatically re run the server 😇  