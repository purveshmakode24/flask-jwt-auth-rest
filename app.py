import datetime
import email
from os import error
from flask import Flask, redirect, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy   # like mongoose for node.js
from flask_migrate import Migrate   # for model change migrations
from flask_marshmallow import Marshmallow  # for object seralization
from marshmallow.fields import Email
from functools import wraps
import jwt  #for creating tokens
from sqlalchemy.orm import defaultload
from werkzeug.security import generate_password_hash, check_password_hash  # for encryption
from flask_mail import Mail, Message
import requests   # Http protocol to make api calls


app = Flask(__name__)

#postgres config
# app.config["SQLALCHEMY_DATABASEURI"] = "postgressql://postgres:1234@locahost/flask-test"
app.config["SECRET_KEY"] = "thisisthesecretkey"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

#for dev purpose
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

#smpt setup
app.config['MAIL_SEVER'] = 'smpt.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'EMAIL_ID'
app.config['MAIL_PASSWORD'] = 'APP_PASSWORD'

mail = Mail(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)


# Authenticated User

user = {
    'username': '',
    'is_autheticated': False,
    'token': ''
    }


# Decorators
def login_token_required(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token is expired.'}), 403
        except:
            return jsonify({'error': 'Token is invalid.'}), 403

        return fn(*args, **kwargs)
    
    return decorator

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<User %r>' % self.username

# Schemas for object serialization
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "date_created")


# Routes      
@app.route("/")
def home():
    users = User.query.all()
    context = {
        'users': users,
        'user': user
        }
    return render_template('index.html', context = context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        payload = {
            "username": request.form['username'],
            "password": request.form['password']
        }

        try:
            r = requests.post('http://127.0.0.1:5000/api/login', payload)
            if r.status_code == 200:
                user['username'] = r.json()['username']
                user['token'] = r.json()['token']
                user['is_authenticated'] = True
                return redirect('/')
            else:
                err = "Inavalid username or Password"
                return render_template('login.html', err=err)
        except:
            return "Some error occurred", 400
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    user['username'] = ""
    user['id_authenticated'] = False
    user['token'] = ""
    return redirect('/')


@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html')

# @app.route('/resetpassword')
# def forgotpassword():
#     return render_template('resetpassword.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/add', methods=['GET', 'POST'])
def addUser():
    globalToastrMsgg = [] # to clear error

    if request.method == 'POST':
        u_name = request.form['username']
        u_email = request.form['email']
        u_password = request.form['password']

        try:
            hashed_password = generate_password_hash(
                u_password, method='sha256'
            )

            user = User(username = u_name, email=u_email, password = hashed_password)

            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding new user."
    else:
        return redirect('/')


@app.route('/delete/<int:userid>')
def deleteUser(userid):
    try:
        user = User.query.get_or_404(userid)
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting a User'


@app.route('/update/<int:userid>', methods=['GET', 'POST'])
def updateUser(userid):
    user = User.query.get(userid)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem Updating a User'
    else:
        return render_template('update.html', user=user)
        

################################# APIs #################################
@app.route('/api/login', methods=['POST'])
def loginAPI():
    auth = request.get_json() or request.form

    try:
        user = User.query.filter_by(username=auth['username']).first()
        if user and check_password_hash(user.password, auth['password']):
            token = jwt.encode({
                'username': user.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }, app.config['SECRET_KEY'])

            return jsonify({'username': user.username, 'token': token}), 400
        return jsonify({'error': 'Incorrect username or password'}), 401   
    except:
        return jsonify({'error': 'Somer error occured'}), 400


@app.route('/api/users', methods=['GET'])
@login_token_required
def getUsersAPI():
    get_users = User.query.all()
    users_schema = UserSchema(many=True)

    users = users_schema.dump(get_users)

    return jsonify({'data': users}), 200


@app.route('/api/addUser', methods=['POST'])
# @login_token_required
def addUserAPI():
    payload = request.get_json()

    try: 
        hashed_password = generate_password_hash(
            payload['password'], method='sha256'
        )

        newuser = User(
            username = payload['username'],
            email = payload['email'],
            password = hashed_password
        )

        db.session.add(newuser)
        db.session.commit()
        return jsonify({'status': 'User added successfully'})
    except:
        return jsonify({'error': 'Somer error occured'}), 400


@app.route('/api/deleteUser', methods=['DELETE'])
@login_token_required
def deleteUserAPI():
    userid = request.args.get('userid') # query params
    usertodelete = User.query.get(userid)
    try: 
        db.session.delete(usertodelete)
        db.session.commit()
        return jsonify({'status': 'User deleted successfully'})
    except:
        return jsonify({'error': 'Somer error occured'}), 400

@app.route('/api/updateUser', methods=['PUT'])
@login_token_required
def updateUserAPI():
    userid = request.args.get('userid') # query params
    payload = request.get_json()
    try: 
        usertoupdate = User.query.get(userid)
        usertoupdate.username = payload['username']
        usertoupdate.email = payload['email']
        db.session.commit()
        return jsonify({'status': 'User updated successfully'})
    except:
        return jsonify({'error': 'Somer error occured'}), 400


@app.route('/api/forgotpassword', methods=['POST'])
# @login_token_required
def forgotPasswordAPI():
    payload = request.get_json() or request.form
    user = User.query.filter_by(email=payload['email']).first()
    
    if user:
        return send_reset_password_mail(user)
    else:
        return jsonify({'error': 'User with that email id does not exist.'}), 400


@app.route('/api/resetpassword/<reset_token>', methods=['GET','POST'])
def resetPasswordAPI(reset_token):
    # reset_token = request.args.get('reset_token') # query params
    if not reset_token:
        return jsonify({'error': 'Token is missing!'}), 403

    try:
        data = jwt.decode(reset_token, app.config['SECRET_KEY'], algorithm=["HS256"])
    except jwt.ExpiredSignatureError:
         return jsonify({'error': 'Link is expired'}), 403
    except:
        return jsonify({'error': 'Link is invalid'}), 403

    if request.method == 'POST':
        user = User.query.filter_by(username=payload['username']).first()
        payload = request.get_json() or request.form
        try:
            new_hashed_password = generate_password_hash(payload['newpassword'], method='sha256')
            user.password = new_hashed_password
            db.session.commit()
            return send_password_reset_successful_mail(user)
        except:
            return jsonify({'error': 'Somer error occured'}), 400
    else:
        return render_template('resetpassword.html', username=data['username'], reset_token = reset_token)


def send_password_reset_successful_mail(user):
    try:
        msg = Message()
        msg.subject = "Password Reset Successful!"
        msg.sender = app.config['MAIL_USERNAME']
        msg.recipients = [user.email]
        msg.body = "Password reset was successful"
        msg.html = f"Password reset was successful!"

        mail.send(msg)
        return jsonify({'status': 'Password successfully changed!'}), 200
    except:
        return jsonify({'error': 'Somer error occured'}), 400


def send_reset_password_mail(user):
    try:
        reset_token = jwt.encode({
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }.  app.config["SECRET_KEY"])

        msg = Message()
        msg.subject = "Password Reset"
        msg.sender = app.config['MAIL_USERNAME']
        msg.recipients = [user.email]
        # msg.html = render_template('reset_email.html', user=user, token=token)
        msg.html = f"<a href='http:localhost:5000/api/resetpassword/{reset_token}'>http:localhost:5000/api/resetpassword/{reset_token}</a>"

        mail.send(msg)
        return jsonify({'status': 'Password reset link has been sent to registered email id'}), 200
    except:
        return jsonify({'error': 'Somer error occured'}), 400
       

if __name__ == '__main__':
    app.run(debug=True)
