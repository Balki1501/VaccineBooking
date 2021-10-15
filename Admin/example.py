from flask import Flask, render_template, request, redirect
from flask.helpers import url_for
from flask_mysqldb import MySQL  # to use db
from flask_mail import Mail, Message
from decouple import config
# API_USERNAME = config('USER')
# API_KEY = config('KEY')
r=[]
Available=250
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


@app.route('/form', methods=['POST'])
def form():
    # name, age, address, phno, email, days = "", 0, "", 0, "", 0
    if request.method == 'POST':
        name = request.form["name"]
        age = request.form["age"]
        address = request.form["address"]
        days = request.form["days"]
        phno = request.form["phno"]
        email = request.form["email"]
        if(days == ""):
            days = 0
            p = (name, age, address, days, phno, email)
            cursor = mysql.connection.cursor()
            print("connected to remotemysql")
            cursor.execute(
                    'INSERT INTO Details(name,age,address,days,phno,email) VALUES (%s,%s,%s,%s,%s,%s)', p)
                
            msg="Thank you for availing the Vaccine. We'll reach you soon via the Mail-id."
        else:
            days = days
            if int(days)>=84:
                p = (name, age, address, days, phno, email)
                cursor = mysql.connection.cursor()
                print("connected to remotemysql")
                cursor.execute(
                    'INSERT INTO Details(name,age,address,days,phno,email) VALUES (%s,%s,%s,%s,%s,%s)', p)
                msg="Thank you for availing the Vaccine. We'll reach you soon via the Mail-id."
            else:
                msg="We are sorry to inform you that You'll need to wait for another "+str(84-int(days))+" days to avail the second dose of the vaccine."
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
    cursor.execute('SELECT name,age,CASE when days>84 then 2 else 1 end as dose,days,email FROM Details ')
    count = 0
    mysql.connection.commit()
    Details = cursor.fetchall()
    count=len(Details)
    return render_template("dashboard.html", Details=Details, count=count)

@app.route("/sendMail",methods=['GET','POST'])
def sendMail():
    global r
    if r!=[]:                                                   #This is to make sure there is only one recipient email
        del r[0]
    if request.method=="POST":
        re=request.form["send"]                                 #Get the data from the form(Email)
        r.append(re)
        sender_mail="balakrishnan1may01@gmail.com"
        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'balakrishnan1may01@gmail.com'
        app.config['MAIL_PASSWORD'] = 'Bala2001$'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        mail = Mail(app)                                        # instantiate the mail class
        msg = Message(
            'Hello',
            sender=sender_mail,
            recipients=r
        )
        msg.body = 'Hi Ena panra???'
        mail.send(msg)                                           #End of code to send Email
    cursor=mysql.connection.cursor()                             #Connect to the server
    cursor.execute("delete from Details where email = '%s';"%re) #To remove record from the server
    mysql.connection.commit()    
    print("Record deleted")   
    global Available
    Available-=1
    return redirect(url_for("dashboard"))                        #To redirect to the same page


if __name__ == '__main__':
    app.run(debug=True)  # debug true will automatically re run the server 😇  
