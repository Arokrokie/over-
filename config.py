import uuid
from flask import Flask
from flask import render_template, request, redirect, url_for, session, make_response, flash
from flask_mail import Mail,Message
from functools import wraps 
import random , json, re, time, string, os, hashlib
from flask_mysqldb import MySQL
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz
import socket
host = socket.gethostname()
app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'arokmayen3@gmail.com'
app.config['MAIL_PASSWORD'] = '0761109871'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

a = app.secret_key = str(uuid.uuid4())
if host == 'DESKTOP-V6NL7VS':
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'acemission'
else:
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'acemission'
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session['role'] == 'Admin':
            return f(*args, **kwargs)
        
        else:
            return make_response(json.dumps({'response': 'Unauthorized access, login required', 'code': 404})), 401
    return decorated_func

# to change on the live server 
def get_time():
    if host == 'DESKTOP-29LVPD6':
        now = datetime.now(pytz.timezone('Africa/Nairobi')).strftime("%Y-%m-%d %I:%M:%S %p")
    else:
        now = datetime.now(pytz.timezone('Africa/Nairobi')).strftime("%Y-%m-%d %I:%M:%S %p")

    return now

def get_filecode():
    code = random.randint(1000000, 9999999)
    return code

app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['IMG_FOLDER'] = 'static/uploads/'
# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# print("the value for a = " +a)


def hash_password(password):
    result = hashlib.sha1('{}'.format(password).encode('utf-8')).hexdigest()
    return result


