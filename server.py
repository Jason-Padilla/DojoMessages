from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt  
import re	
import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
ALPHA_ONLY = re.compile(r'^[a-zA-Z]+$')

@app.route('/')
def index():
    if "DojoMessages-id" in session:
        id = session["DojoMessages-id"]
        return redirect(f"/{id}/messages")
    else:
        return render_template("login-regis.html")

@app.route("/register/email-realtime", methods=['POST'])
def email_realtime():
    found = False
    mysql = connectToMySQL('DojoMessages_Flask')        # connect to the database
    query = "SELECT * from users WHERE email = %(em)s;"
    data = { 'em': request.form['regis-email'] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    
    return render_template('partials/email-realtime.html', found=found)  # render a partial and return it
    
@app.route('/register',methods=['POST'])
def register():
    #Check to see if it is in a valid email format
    if not ALPHA_ONLY.match(request.form['first-name']):
        flash("     Enter a valid first name.", "first-name" )
    if not ALPHA_ONLY.match(request.form['last-name']):
        flash("     Enter a valid last name.", "last-name" )
    if not EMAIL_REGEX.match(request.form['regis-email']):  
        flash("     Enter a valid email address.","regis-email")
    if len(request.form['regis-password']) < 1:
        flash("Enter a valid password.","regis-password")
    if '_flashes' in session.keys():
        return redirect("/")
    else:
        #Check to see if the email is avaiable
        query = "SELECT * FROM users WHERE email = %(em)s"
        data = {'em': request.form['regis-email']}
        mysql = connectToMySQL('DojoMessages_Flask')
        user = mysql.query_db(query,data)

        if len(user) >= 1:
            flash("Email already in use, please try another.",'regis-email')
            return redirect("/")
        #If email not in use then add it to the database
        else:
            pw_hash = bcrypt.generate_password_hash(request.form['regis-password'])  
            mysql = connectToMySQL('DojoMessages_Flask')
            query = "INSERT INTO users (first_name,last_name,email,password,created_at,updated_at) VALUES (%(fn)s,%(ln)s,%(em)s,%(pw)s,NOW(),NOW());"
            data = {'fn': request.form['first-name'],
                    'ln': request.form['last-name'],
                    'em': request.form['regis-email'],
                    'pw': pw_hash}
            #When INSERT into a table the result returns the id not the full object
            id = mysql.query_db(query,data)
            session['DojoMessages-id'] = id
            return redirect(f"/{id}/messages")

@app.route('/login',methods=['POST'])
def login():
    mysql = connectToMySQL("DojoMessages_Flask")
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data = { "em" : request.form["login-email"] }
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['login-password']):
            session['DojoMessages-id'] = result[0]['id']
            id = result[0]['id']
            return redirect(f'/{id}/messages')
        else:
            flash("Incorrect password.","login-password")
            return redirect("/")
    else:
        flash("Enter a valid email.","login-email")
        return redirect("/")

@app.route('/<id>/messages')
def message_board(id):
    
    if 'DojoMessages-id' in session:
        query = "SELECT * FROM users WHERE id = %(id)s"
        data = {'id': id}
        mysql = connectToMySQL('DojoMessages_Flask')
        profile = mysql.query_db(query,data)

        query2 = "SELECT * FROM users WHERE id != %(id)s"
        data2 = {'id': id}
        mysql2 = connectToMySQL('DojoMessages_Flask')
        users = mysql2.query_db(query2,data2)

        query3 = "SELECT * FROM messages WHERE users_id = %(id)s"
        data3 = {'id': id}
        mysql3 = connectToMySQL('DojoMessages_Flask')
        messages = mysql3.query_db(query3,data3)
        for message in messages:
            message['created_at'] = message['created_at'].strftime("%m/%d/%Y")

        return render_template("wall.html",profile = profile[0],users = users, messages = messages, amount = len(messages))
    else:
        return redirect('/')

@app.route('/<id>/messages/send-message',methods = ['POST'])
def send_message(id):
    mysql = connectToMySQL('DojoMessages_Flask')
    query = "INSERT INTO `messages` (`message`, `users_id`, `from`, `from_id`) VALUES (%(msg)s,%(uid)s,%(frm)s,%(frmid)s);"
    data = {'msg': request.form['message'],
            'uid': request.form['to-id'],
            'frm': request.form['from'],
            'frmid': id}
    message = mysql.query_db(query,data)
    #render_template('partials/send-realtime.html') if we wanted a partial
    return redirect(f'/{id}/messages')

@app.route('/delete/message',methods = ['POST'])
def delete_message(): 
    mysql = connectToMySQL('DojoMessages_Flask')
    query = "DELETE FROM `messages` WHERE id = %(mid)s;"
    data = {"mid": request.form['message-id']}
    mysql.query_db(query,data)

    id = session['DojoMessages-id']
    #render_template('partials/delete-realtime.html') if we wanted a partial
    return redirect(f"/{id}/messages")

@app.route('/logout')
def logout(): 
    if 'DojoMessages-id' in session:
        session.pop('DojoMessages-id')
        return redirect('/')
    else:
        return redirect('/')

if __name__ == "__main__":
    app.run(port=5004,debug=True) 