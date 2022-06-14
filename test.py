from cgi import test
from urllib import response
from app import app, querry_starred_books, validate_password
import unittest


class FlaskTest(unittest.TestCase):

    # Checking the index page response 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)
    
    # Checking Login Page loaded Correctly
    def test_login_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login',content_type='html/text')
        self.assertTrue(b'LOGIN' in response.data)
    
    # Checking Forgot Password Page loaded Correctly
    def test_forgot_password_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/forgotpassword',content_type='html/text')
        self.assertTrue(b'FORGOT PASSWORD' in response.data)
    
    #Ensuring forgot password behaves correctly given the correct credentials
    def test_correct_forgot_password(self):
        tester = app.test_client(self)
        response = tester.post('/forgotpassword', data=dict(email='asdfg@gmail'), follow_redirects=True)
        self.assertTrue(b'Email has been sent' and b'Please check your email for the reset password link.' in response.data)
        
    # Checking Favorites Page loaded Correctly
    def test_favorites_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/favorites',content_type='html/text')
        self.assertTrue(b'Favorite Books' and b'Recommended Books', response.data)
    
    # Checking Home Page loaded Correctly
    def test_home_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/',content_type='html/text')
        self.assertTrue(b'Books' and b'Get Recommendations', response.data)
    
    # Checking Signup Page loaded Correctly
    def test_signup_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/signup',content_type='html/text')
        self.assertTrue(b'SIGNUP' and b'Name' and b'Username' and b'Surname' and b'Email' and b'Password' and b'Submit', response.data)
        
    #Ensuring login behaves correctly given the correct credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email='asdfg@gmail.com', password = 'asdfg'), follow_redirects=True)
        self.assertTrue(b'Books' and b'ewig geliebt', response.data)
        
    #Ensuring signup behaves correctly given the correct credentials
    def test_correct_signup(self):
        tester = app.test_client(self)
        response = tester.post('/signup', data=dict(email='bbbbb@gmail.com', password = 'bbbbb', username='bbbbb', surname ='bbbbb', name='bbbbb'), follow_redirects=True)
        self.assertTrue(b'Books' and b'ewig geliebt', response.data)
        
    #Ensure login behaves correctly given the incorrect credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email='asdfg', password = 'asdfg'), follow_redirects=True)
        self.assertIn(b'Incorrect email or password', response.data)
        
    #Ensure signup behaves correctly given the incorrect credentials
    def test_incorrect_signup_with_no_valid_email(self):
        tester = app.test_client(self)
        response = tester.post('/signup', data=dict(email='bbbbb@s', password = 'bbbbb', username='bbbbb', surname ='bbbbb', name='bbbbb'), follow_redirects=True)
        self.assertIn(b"Please enter a valid email",response.data)  
        
    #Ensure that querry_starred_books function returns a list
    def test_querry_starred_books(self):
        c = querry_starred_books(1)
        self.assertEqual(type(c).__name__,'list')
        
    #Ensure that validate_password function returns correct response
    def test_validate_password(self):
        c = validate_password("abcdef","abcdef")
        self.assertEqual(c,True)
    
    #Ensure that validate_password function returns correct response
    def test_validate_password2(self):
        c = validate_password("abc","abc")
        self.assertEqual(c,"Password must be at least 5 characters")
        
    #Ensure that validate_password function returns correct response
    def test_validate_password3(self):
        c = validate_password("abcdef","abc")
        self.assertEqual(c,"Passwords do not match")
    
    #Ensure that validate_password function returns correct response    
    def test_validate_password4(self):
        c = validate_password("abcdef")
        self.assertEqual(c,True)
    
    #Ensure that validate_password function returns correct response
    def test_validate_password5(self):
        c = validate_password("abc")
        self.assertEqual(c,"Password must be at least 5 characters")    
    
    #Ensure that validate_password function returns correct response
    def test_validate_password6(self):
        c = validate_password("aaaaaaaaaaaaaaaaaaaaaa")
        self.assertEqual(c,"Passwrod must be max of 20 characters") 
        
    #Ensure that validate_password function returns correct response
    def test_validate_password7(self):
        c = validate_password("aaaaaaaaaaaaaaaaaaaaaa","aa")
        self.assertEqual(c,"Passwrod must be max of 20 characters") 
        
    #Ensure logout behaves correctly
    def test_logout(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(email='asdfg@gmail.com', password = 'asdfg'), follow_redirects=True)    
        response = tester.get('/logout',follow_redirects=True)
        self.assertIn(b'Home',response.data)
    
    #Ensure that favorites page requires login
    def test_main_route_requires_login(self):
        tester = app.test_client(self)
        response = tester.get('/favorites', follow_redirects=True)    
        self.assertTrue(b'SIGNUP',response.data)
        
    #Ensure that books show up on the main page
    def test_books_show_up(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(email='asdfg@gmail.com', password = 'asdfg'), follow_redirects=True)
        self.assertIn(b'ewig geliebt', response.data)
        
if __name__ == 'main':
    unittest.main()
