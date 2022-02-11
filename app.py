from flask import Flask, render_template, request, redirect, session, make_response, jsonify, url_for
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import re
from flask_session import Session
from flask_cors import CORS
from threading import Thread
import jwt
from time import time
from os import environ
from numpy import load

load_data = environ.get("LOAD_DATA")
cos_sim = None
if load_data:
    print('Loading data...')
    filename = 'transform_result_reduced.npz'
    loaded = load(filename)
    cos_sim = loaded['arr_0']
    print('Data is loaded!')

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "johnistheking922@gmail.com"
app.config['MAIL_PASSWORD'] = environ.get("MAIL_PASSWORD")
mail = Mail(app)

BOOK_RECOM_ENV = environ.get("BOOK_RECOM_ENV")
if BOOK_RECOM_ENV == 'prod':
    app.config = environ.get("JAWSDB_URL")
    app.debug = False
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/recomm_system'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)
CORS(app)

db = SQLAlchemy(app)

@app.before_first_request
def setup():
    db.create_all()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def get_reset_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id,
                        'exp': time() + expires_in},
                        key='secret', algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, 'secret', algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __init__(self, name, surname, username, email, password):
        self.name = name
        self.surname = surname
        self.username = username
        self.email = email
        self.password = password

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    author = db.Column(db.String(40), nullable=False)
    publisher = db.Column(db.String(40), nullable=False)
    maintopic = db.Column(db.String(40))
    subtopics = db.Column(db.String(50))

    def __init__(self, title, author, publisher, maintopic, subtopics):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.maintopic = maintopic
        self.subtopics = subtopics
    
class UserFavorites(db.Model):
    __tablename__ = 'user_favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    def __init__(self, user_id, book_id):
        self.user_id = user_id
        self.book_id = book_id

@app.route('/', methods=['GET'], defaults={"page": 1})
@app.route('/<int:page>', methods=['GET'])
def index(page):
    page = page
    per_page = 10
    books = Book.query.paginate(page,per_page,error_out=False)
    return render_template('home.html', title='Book Recommendation System', books=books)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if 'logged_in' not in session or ('logged_in' in session and session['logged_in'] != True):
        return redirect('/')
    if request.method == 'GET':
        return render_template('signup.html', title='Signup')
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        validation_result = validate_user_data(name, surname, username, email, password)
        if validation_result == '':
            data = User(name, surname, username, email, password)
            db.session.add(data)
            db.session.commit()
            session['logged_in'] = True
            session['userid'] = data.id
            session['username'] = data.username
            return redirect('/')
        else:
            return render_template('signup.html', title='Signup', validation_msg=validation_result)

def validate_password(pswd, pswd_cnfrm=None):
    if (len(pswd) < 5):
        return 'Password must be at least 5 characters'
    elif (len(pswd) > 20):
        return 'Passwrod must be max of 20 characters'
    elif (pswd_cnfrm != None and pswd != pswd_cnfrm):
        return 'Passwords do not match'
    else:
        return True

def validate_user_data(name, surname, username, email, password):
    if (len(name) == 0 or len(name) > 20):
        return 'Name must be 1-20 characters'
    if (len(username) == 0 or len(username) > 20):
        return 'Username must be 1-20 characters'
    if not (re.match(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)):
        return 'Please enter a valid email'
    if db.session.query(User).filter(User.username == username).count() > 0:
        return 'This username is already registerd'
    if db.session.query(User).filter(User.email == email).count() > 0:
        return 'This email is already registered'
    pswd_validation = validate_password(password)
    if (pswd_validation != True):
        return pswd_validation
    return ''

@app.route('/change-password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        if 'logged_in' not in session or ('logged_in' in session and session['logged_in'] != True):
            return redirect('/signup')
        content = request.json
        old_pswd = content['old-pswd']
        new_pswd = content['new-pswd']
        new_pswd_confirm = content['cnfrm-pswd']
        user = User.query.get(int(session['userid']))
        if user and user.password == old_pswd:
            if new_pswd != new_pswd_confirm:
                return custom_message('Confirmed password does not match', 400)
            else:
                user.password = new_pswd
                print('old pswd:', old_pswd)
                print('new pswd:', new_pswd)
                print('must be new:', user.password)
                print('User password:', user.password)
                db.session.commit()
                return custom_message('Your password has been changed!', 200)
        else:
            return custom_message('Incorrect password', 400)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session and session['logged_in'] == True:
        return redirect('/')
    login_msg = None
    if request.method == 'GET':
        return render_template('login.html', title='login')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['userid'] = user.id
            session['username'] = user.username
            return redirect('/')
        else:
            login_msg = 'Incorrect email or password'
    
    return render_template('login.html', login_msg=login_msg, title='login')

@app.route('/logout')
def logout():
    session['logged_in'] = None
    session['userid'] = None
    session['username'] = None
    return redirect('/')

@app.route('/fav/<int:id>', methods=['GET'])
def toggle_fav(id):
    if 'logged_in' not in session or ('logged_in' in session and session['logged_in'] != True):
        return custom_message('Authentication failed', 404)
    user_id = session['userid']
    book_id = id
    faved_book = UserFavorites.query.filter_by(user_id=user_id, book_id=book_id).first()
    if faved_book:
        UserFavorites.query.filter_by(user_id=user_id, book_id=book_id).delete()
        msg = 'Book deleted from favorites'
    else:
        msg = 'Book added to favorites'
        user_fav = UserFavorites(user_id, book_id)
        db.session.add(user_fav)
    print(msg)
    db.session.commit()
    return custom_message(msg, 200)

@app.route('/favorites')
def favorites():
    if 'logged_in' not in session or ('logged_in' in session and session['logged_in'] != True):
        return redirect('/signup')
    user_id = session.get('userid')
    fav_books = UserFavorites.query\
        .filter_by(user_id=user_id)\
        .join(Book, UserFavorites.book_id==Book.id)\
        .add_columns(Book.id, Book.title, Book.author, Book.publisher, Book.maintopic, Book.subtopics)\
        .all()
    recommended_books = []
    for fav_book in fav_books:
        rec_books = recommend_books(id=fav_book.id, num_of_recs=3)
        filtered_rec_books = list(filter(lambda rec_book: rec_book.title not in list(map(lambda x: x.title, fav_books)), rec_books))
        if len(filtered_rec_books) > 0:
            recommended_books.append(filtered_rec_books[0])
        
    return render_template('favorites.html', title='Favorites', fav_books=fav_books, recommended_books=recommended_books)

def send_email(subject, recipent, body, html):
    with app.app_context():
        msg = Message()
        msg.subject = subject
        msg.recipients = [recipent]
        msg.sender = 'johnistheking922@gmail.com'
        msg.body = body
        msg.html = html
        mail.send(msg)

# GET: Forgot password page for submitting the request
# POST: Sends the password reset instructions mail
@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html', title='Forgot Password')
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                token = user.get_reset_token()
                print(token)
                Thread(target=send_email, args=(
                    'Password Reset Instructions',
                    email,
                    render_template('email/reset_password.txt',
                        user=user,
                        token=token),
                    render_template('email/reset_password.html',
                        user=user,
                        token=token))).start()
            except Exception as e:
                print(e)
                return custom_message('An error occured while sending the email', 404)
        return render_template('email_sent.html', title='Email sent!')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'logged_in' in session and session['logged_in'] == True:
        print('User is already logged in')
        print(session['logged_in'])
        return redirect('/')
    user = User.verify_reset_password_token(token)
    if not user:
        return custom_message('Invalid token. Please get a new reset token', 403)
    print(request.method)
    if request.method == 'GET':
        return render_template('reset_password.html',token=token,title='Reset Password')
    else:
        content = request.json
        pswd = content['pswd']
        pswd_cnfrm = content['pswd-cnfrm']
        validated = validate_password(pswd, pswd_cnfrm)
        if validated == True:
            return custom_message('You password has been changed', 200)
        else:
            return custom_message(validated, 400)

def recommend_books(title='', id=None, num_of_recs=1):
    if (id != None):
        book_id = id
    else:
        book = Book.query.filter_by(title=title).first()
        book_id = book.id
    id_inbounds = book_id < 4000 #todo increase later
    if book_id and num_of_recs > 0 and id_inbounds:
        cos_sim_index = book_id - 1 # cos_sim index starts from 0 while db from 1
        sim_scores = list(enumerate(cos_sim[cos_sim_index]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:num_of_recs+1]
        book_ids = [i[0]+1 for i in sim_scores] # reincrement for ids
        books = Book.query.filter(Book.id.in_(book_ids)).all()
        return books
    return []

def custom_message(message, status_code): 
    return make_response(jsonify(message), status_code)

if __name__ == '__main__':
    app.run()
