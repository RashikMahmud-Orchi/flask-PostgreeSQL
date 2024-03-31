from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'xyzsdfg'
app.config['UPLOAD_FOLDER'] = './uploaded_images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://orchi:r9ybSlSOVM5ADl968LrKdBS6p8cftbdx@dpg-cnsjdk8l5elc73fkuo5g-a/user_e3f9'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User Model
class User(db.Model):
    __tablename__ = 'user'  # Specify the actual table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)




# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to load OpenAI model and get responses
def get_gemini_response(input, image):
    # Implementation of this function was missing in the provided code
    pass

# Function to save user credentials to the database
def save_user_credentials_to_db(email, password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'loggedin' in session:
        # User is already logged in, show the index page
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            input_prompt = request.form['input_prompt']
            
            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Process the image and get response
                image = Image.open(file_path)
                response = get_gemini_response(input_prompt, image)
                
                image_url = url_for('static', filename=filename)
                
                # Pass the response and image URL to the template
                return render_template('index.html', response=response, image_url=image_url)

        # Initial page load or no file uploaded
        return render_template('index.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        # For demonstration purposes, checking credentials by querying the database
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['loggedin'] = True
            session['email'] = email
            message = "Logged in successfully!"
            return redirect(url_for('index'))  # Redirect to index page on successful login

        message = "Please enter correct email / password!"

    return render_template('login.html', message=message)  # Pass the message variable to the template

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        # For demonstration purposes, storing credentials in the database
        save_user_credentials_to_db(email, password)
        message = 'You have successfully registered!'
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    elif request.method == 'POST':
        message = 'Please fill out the form!'

    return render_template('register.html', message=message)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
