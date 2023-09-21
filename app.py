from sqlite3 import Row
from config import *
from flask import render_template, request, redirect, url_for, session, make_response
import json
import MySQLdb.cursors
from datetime import datetime
from werkzeug.utils import secure_filename
import re

# format currency
@app.template_filter()
def currency_format(value):
    value = float(value)
    return "{:,.0f}".format(value)

#split page
@app.template_filter()
def par_format(value):
    x = value.split(",")
    return x

@app.route('/index')
@app.route('/')
def index():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM events ORDER BY eve_id DESC LIMIT 2 ")
        events = cursor.fetchall()
        cursor.execute("SELECT * FROM services ORDER BY ser_id DESC LIMIT 2")
        rows=cursor.fetchall()
        res = { 'status': 'true', 'rows': rows, 'events': events,}
        return render_template('index.html', **res)


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['email'] = account['email']
            session['role'] = account['role']
            session['username'] = account['username']
            session['name'] = account['name']
            session['phone'] = account['phone']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email or password'
            return render_template('login.html', error=msg)
    # Show the login form with message (if any)
    else:
        return render_template('login.html', error=msg)



@app.route('/register', methods=['POST', 'GET'])
def register():
    # `user_id`, `fname`, `lname`, `phone`, `email`, `password`
    msg = ''
    # applying empty validation
    if request.method == 'POST':
        # passing HTML form data into python variable.
        c = request.form['name']
        f = request.form['username']
        a = request.form['phone']
        g = request.form['email']
        h = request.form['password']
        r = 'user'
       
        # `user_id`, `name`, `username`, `phone`, `email`, `password`, `role`
        
        # creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # query to check given data is present in database or no
        cursor.execute('SELECT * FROM  users')

        # executing query to insert new data into MySQL
        cursor.execute(
            'INSERT INTO  users VALUES (NULL, %s, %s,%s,%s,%s,%s)', (c, f, a, g, h, r))
        mysql.connection.commit()

        # displaying message
        msg = 'You have successfully registered !'
        res = {'msg': 'You have successfully registered !'}
        return redirect('/login')
        # return render_template('students-records.html')
    else:
        return render_template('register.html', msg=msg)


@app.route('/dashboard')
@login_required
def dashboard():
    if "email" in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM services order by services.ser_id DESC")
    rows=cursor.fetchall()
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM services order by services.ser_id DESC")
    rows=cursor.fetchall()
    cursor.execute("SELECT * FROM donations ORDER BY don_id DESC LIMIT 1")
    donations=cursor.fetchall()
    res = {"data" : rows, 'donations':donations}
    return render_template('services.html', **res)

@app.route('/blog')
def blog():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM blogs order by blogs.blog_id DESC")
    rows=cursor.fetchall()
    res = {"data" : rows}
    return render_template('blog.html', **res)




#Edit || Update Account... 
@app.route('/read/<blog_id>', methods=['POST', 'GET'])
def read_blog (blog_id):
    
    if request.method == 'GET':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM blogs WHERE blog_id=%s", (blog_id,))
        data = cur.fetchall()
        response = {'data' : data}
        return render_template('readpost.html', **response) 

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')



@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/blog_upload', methods=['POST', 'GET'])
def blog_upload():
    if request.method == 'POST':
        # check if the post request has the file part, `
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.split(".")[-1]
            filename = '{}.{}'.format(get_filecode(), file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = request.form['name']
            title = request.form['title']
            date=get_time()
            author = request.form['author']
            blogbody = request.form['blogbody']
            img = app.config['IMG_FOLDER'] + str(filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM  blogs WHERE name=%s LIMIT 1", (name, ))
            rows = cursor.fetchone()
            if not rows:
                sql_query = "INSERT INTO  blogs(name,title,date,author,img, blogbody) " \
                            "VALUES(%s, %s, %s, %s, %s, %s)"
                bind_data = (name,title,date,author,img, blogbody, )
                cursor.execute(sql_query, bind_data)
                mysql.connection.commit()
                flash('Record successfully added')
                return redirect(url_for('blog'))
            else:
                flash('Records already registered')
                return redirect(url_for('blog'))
        else:
            flash('Allowed file types png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM blogs")
        data = cursor.fetchall()
        return render_template('blog_upload.html', data=data)

    



    
@app.route('/profile', methods=['POST', 'GET'])
def profile():   
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users order by users.user_id DESC")
        rows=cursor.fetchall()
        res = {"data" : rows}
        return render_template('profile.html', **res)

#Edit || Update Account... 
@app.route('/edit/<user_id>', methods=['POST', 'GET'])
def edit_entry (user_id):
    
    if request.method == 'GET':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        data = cur.fetchall()
        response = {'data' : data, 'status' :  'true', }
        return render_template('edit_profile.html', **response) 
    else:
        # `user_id`, `name`, `username`, `phone`,`email`
        # a = request.form['std_id']   
        x = request.form['name']
        f = request.form['username']
        g = request.form['email']
        h = request.form['phone']
      
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET name = %s, username = %s, email = %s, phone = %s WHERE user_id = %s ',(x, f, g, h, (user_id), ))
        mysql.connection.commit()
        return redirect('/profile')

@app.route('/logout')
def logout():
    if "email" in session:
        session.pop('username', None)
        session.pop("name",None)
        return redirect(url_for('login'))
    else:
        return redirect('login')

    




@app.route('/gallery')
def gallery():
     if "email" in session:
    # Get a list of all uploaded image files
        images = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('gallery.html', images=images)
     else:
        return redirect('/login')

@app.route('/uploadimg', methods=['GET', 'POST'])
def img():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        return redirect('/gallery')
    
    return render_template('uploadimg.html')
     
@app.route('/update/<user_id>', methods=['POST', 'GET'])
def edit_profile (user_id):
    
    if request.method == 'GET':
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        data = cur.fetchall()
        response = {'data' : data, 'status' :  'true', }
        return render_template('uploadprof.html', **response) 
    else:
        # `user_id`, `name`, `username`, `phone`,`email`
        # a = request.form['std_id']   
        x = request.files['pic']
        
       
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE users SET pic = %s WHERE user_id = %s ',(x, (user_id), ))
        mysql.connection.commit()
        return redirect('/profile')


@app.route('/donate', methods=['POST', 'GET'])
def donate():
    # `user_id`, `fname`, `lname`, `phone`, `email`, `password`
    msg = ''
    # applying empty validation
    if request.method == 'POST':
        # passing HTML form data into python variable.
        c = request.form['name']
        g = request.form['email']
        h = request.form['phone']
        k = float(request.form['amount'])
        # creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # query to check given data is present in database or no
        cursor.execute('SELECT * FROM  donations')

        # executing query to insert new data into MySQL
        cursor.execute(
            'INSERT INTO  donations VALUES (NULL, %s, %s,%s,%s)', (c, g, h, k))
        mysql.connection.commit()

        # displaying message
        msg = 'You have successfully registered !'
        res = {'msg': 'You have successfully registered !'}
        return redirect('/payment')
        # return render_template('students-records.html')
    else:
        return render_template('donate.html', msg=msg)

@app.route('/donations')
def donations():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM donations order by donations.don_id DESC")
    rows=cursor.fetchall()
    res = {"data" : rows}
    return render_template('donations.html', **res)


@app.route('/events')
def events():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM events order by events.eve_id DESC")
    rows=cursor.fetchall()
    res = {"data" : rows}
    return render_template('events.html', **res)



@app.route('/service_upload', methods=['POST', 'GET'])
def service_upload():
    if request.method == 'POST':
        # check if the post request has the file part, `
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.split(".")[-1]
            filename = '{}.{}'.format(get_filecode(), file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = request.form['name']
            title = request.form['title']
            date=get_time()
            place = request.form['place']
            blogbody = request.form['blogbody']
            img = app.config['IMG_FOLDER'] + str(filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM  services WHERE name=%s LIMIT 1", (name, ))
            rows = cursor.fetchone()
            if not rows:
                sql_query = "INSERT INTO  services(name,title,date,place,img, blogbody) " \
                            "VALUES(%s, %s, %s, %s, %s, %s)"
                bind_data = (name,title,date,place,img, blogbody, )
                cursor.execute(sql_query, bind_data)
                mysql.connection.commit()
                flash('Record successfully added')
                return redirect(url_for('services'))
            else:
                flash('Records already registered')
                return redirect(url_for('services'))
        else:
            flash('Allowed file types png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM services")
        data = cursor.fetchall()
        return render_template('service_upload.html', data=data)
    
    
@app.route('/events_upload', methods=['POST', 'GET'])
def events_upload():
    if request.method == 'POST':
        # check if the post request has the file part, `
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.split(".")[-1]
            filename = '{}.{}'.format(get_filecode(), file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            name = request.form['name']
            title = request.form['title']
            date=get_time()
            place = request.form['place']
            blogbody = request.form['blogbody']
            img = app.config['IMG_FOLDER'] + str(filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM  events WHERE name=%s LIMIT 1", (name, ))
            rows = cursor.fetchone()
            if not rows:
                sql_query = "INSERT INTO  events(name,title,date,place,img, blogbody) " \
                            "VALUES(%s, %s, %s, %s, %s, %s)"
                bind_data = (name,title,date,place,img, blogbody, )
                cursor.execute(sql_query, bind_data)
                mysql.connection.commit()
                flash('Record successfully added')
                return redirect(url_for('events'))
            else:
                flash('Records already registered')
                return redirect(url_for('events'))
        else:
            flash('Allowed file types png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM events")
        data = cursor.fetchall()
        return render_template('events_upload.html', data=data)


@app.route('/payment')
def payment():
    return render_template('payment.html')



@app.route('/send_email', methods=['POST','GET'])
def send_email():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        email = request.form['email']
        msg = request.form['msg']

        message = Message(subject,sender=[email], recepient='arokmayen3@gmail.com')

        message.body = msg

        message.send(message)

        success = 'Message Sent'

        return render_template('contact.html', success=success)
            
            
            
@app.route('/profile_upload', methods=['GET', 'POST'])
def profile_upload():
    if request.method == 'POST':
        # check if the post request has the file part, `
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.split(".")[-1]
            filename = '{}.{}'.format(get_filecode(), file_ext)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            stid = str(request.form['user_id'])
            img = app.config['IMG_FOLDER'] + str(filename)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM users WHERE users.user_id=%s", (stid))
            rows = cursor.fetchone()
            if not rows:
                sql_query = "INSERT INTO  userimages (img,stid) " \
                            "VALUES(%s,%s)"
                bind_data = (img,stid)
                cursor.execute(sql_query, bind_data)
                mysql.connection.commit()
                flash('Record successfully added')
                return redirect(url_for('profile'))
            else:
                flash('Records already registered')
                return redirect(url_for('profile'))
        else:
            flash('Allowed file types png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM userimages f INNER JOIN users s WHERE f.user_id=s.user_id")
        data = cursor.fetchall()
        cursor.execute("SELECT * FROM users order by name ")
        rows = cursor.fetchall()
        response = {'data': data, 'status': 'true', 'rows': rows,}
        return render_template('profile_upload.html', **response)

if __name__ == '__main__': 
    app.run(debug=True)