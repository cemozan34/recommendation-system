from flask import Flask, render_template, request, redirect, session, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
from flask_session import Session
from flask_cors import CORS

app = Flask(__name__)

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/recomm_system'
else:
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)
CORS(app)
# session.app.session_interface.db.create_all()

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

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
    if session['logged_in'] == True:
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
            return render_template('home.html', title='Book Recommendation System')
        else:
            return render_template('signup.html', title='Signup', validation_msg=validation_result)

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
    if (len(password) < 5 or len(password) > 20):
        return 'Password must be at least 5 max of 20 characters.'
    return ''

@app.route('/change-password', methods=['POST'])
def change_password():
    change_psw_msg = None
    if request.method == 'POST':
        if not session['logged_in']:
            return redirect('/signup')
        old_pswd = request.form['old-pswd']
        new_pswd = request.form['new-pswd']
        new_pswd_confirm = request.form['cnfrm-pswd']
        user = User.query.get(int(session['userid']))
        if user and user.password == old_pswd:
            if new_pswd != new_pswd_confirm:
                change_psw_msg = 'Confirmed password does not match'
            else:
                user.password = new_pswd
                print('old pswd:', old_pswd)
                print('new pswd:', new_pswd)
                print('must be new:', user.password)
                db.session.commit()
                change_psw_msg = 'Your password has been changed!'
        else:
            change_psw_msg = 'Incorrect password'
    print(user.password)
    return render_template('home.html', change_psw_msg=change_psw_msg, title='Book Recommendation System')

def validate_password():
    return None #Todo

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['logged_in'] == True:
        return redirect('/')
    login_msg = None
    if request.method == 'GET':
        return render_template('login.html', title='login')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                session['logged_in'] = True
                session['userid'] = user.id
                session['username'] = user.username
                return redirect('/')
            else:
                login_msg = 'Incorrect password'
        else:
            login_msg = f'User with email {email} is not found.'
    
    return render_template('login.html', login_msg=login_msg, title='login')

@app.route('/logout')
def logout():
    session['logged_in'] = None
    session['userid'] = None
    session['username'] = None
    return redirect('/')

@app.route('/fav/<int:id>', methods=['GET'])
def toggle_fav(id):
    if not session.get('logged_in'):
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
    if not session.get('logged_in'):
        return redirect('/signup')
    user_id = session.get('userid')
    fav_books = UserFavorites.query\
        .filter_by(user_id=user_id)\
        .join(Book, UserFavorites.book_id==Book.id)\
        .add_columns(Book.title, Book.author, Book.publisher, Book.maintopic, Book.subtopics)\
        .all()
    print(fav_books[0])
    return render_template('favorites.html', fav_books=fav_books)

def custom_message(message, status_code): 
    return make_response(jsonify(message), status_code)

if __name__ == '__main__':
    app.run()
