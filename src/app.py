from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
import re
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
import base64
import os

app = Flask(__name__)


# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key_here"
app.config['SECRET_KEY'] = os.urandom(24)


db = SQLAlchemy(app)
jwt = JWTManager(app)

#User Database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

#database to store key:value
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', back_populates="data")

#User-Data Relationship
User.data = db.relationship('Data', back_populates="user")

# inject user status[Is user logged in or not] 
@app.context_processor
def inject_user_status():
    user_logged_in = 'user_id' in session
    return dict(user_logged_in=user_logged_in)

#Just a test route
@app.route("/")
def index():
    return "Hello World"

#The Register Route
@app.route("/api/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            data = request.form
            #All the neccesary error codes are mentioned 
            required_fields = ("username", "email", "password", "full_name", "age", "gender")
            if not all(key in data for key in required_fields):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": "Invalid request. Please provide all required fields: username, email, password, full_name, age, gender."
                }), 400

            if User.query.filter_by(username=data['username']).first():
                return jsonify({
                    "status": "error",
                    "code": "USERNAME_EXISTS",
                    "message": "The provided username is already taken. Please choose a different username."
                }), 409

            if User.query.filter_by(email=data['email']).first():
                return jsonify({
                    "status": "error",
                    "code": "EMAIL_EXISTS",
                    "message": "The provided email is already registered. Please use a different email address."
                }), 409

            if len(data['password']) < 8 or not re.search(r'[A-Z]', data['password']) or \
                    not re.search(r'[a-z]', data['password']) or not re.search(r'\d', data['password']) or \
                    not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['password']):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_PASSWORD",
                    "message": "Password must be at least 8 characters long and contain an uppercase letter, lowercase letter, number, and special character."
                }), 400

            if not data['age'] or int(data['age']) <= 0:
                return jsonify({
                    "status": "error",
                    "code": "INVALID_AGE",
                    "message": "Invalid age value. Age must be a positive integer."
                }), 400

            if not data['gender'].strip():
                return jsonify({
                    "status": "error",
                    "code": "GENDER_REQUIRED",
                    "message": "Gender field is required. Please specify the gender."
                }), 400

            #password is hased theough bcrypt and then encoded to base64
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = base64.b64encode(hashed_password).decode('utf-8')

            new_user = User(
                username=data['username'],
                email=data['email'],
                password=hashed_password_str,
                full_name=data['full_name'],
                age=int(data['age']),
                gender=data['gender']
            )

            db.session.add(new_user)
            db.session.commit()

            message = {
                "status": "success",
                "message": "User successfully registered!",
                "data": {
                    "user_id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "age": new_user.age,
                    "gender": new_user.gender
                }
            }
            return render_template('register.html', message=message)
        except:
            message = {
                "status": "error",
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred. Please try again later."
            }
            return render_template('register.html', message=message)
        
    return render_template("register.html")
    

#Route for token generation
@app.route("/api/token", methods=["POST", "GET"])
def generate_token():
    if request.method == "POST":
        try:
            data = request.form.to_dict()

            # Check for missing fields
            if not all(key in data for key in ["username", "password"]):
                return jsonify({
                    "status": "error",
                    "code": "MISSING_FIELDS",
                    "message": "Missing fields. Please provide both username and password."
                }), 400

            user = User.query.filter_by(username=data['username']).first()

            # Validate credentials
            if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), base64.b64decode(user.password)):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid credentials. The provided username or password is incorrect."
                }), 401
            
            access_token = create_access_token(identity=str(user.id))

            # Debugging: Check if access_token is generated
            app.logger.info(f"Generated Access Token: {access_token}")

            message = {
                "status": "success",
                "message": "Access token generated successfully.",
                "data": {
                    "access_token": access_token,
                    "expires_in": 3600
                }
            }
            return render_template("generate_token.html", message=message)
        except Exception as e:
            # Log the error for debugging
            app.logger.error(f"Error occurred while generating token: {str(e)}")
            
            message = {
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": "Internal server error occurred. Please try again later."
            }
            return render_template("generate_token.html", message=message)
        
    return render_template("generate_token.html")
        

#Route for Login
@app.route("/api/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.form.to_dict()

            # Check for missing fields
            if not all(key in data for key in ["username", "password", "access_token"]):
                return jsonify({
                    "status": "error",
                    "code": "MISSING_FIELDS",
                    "message": "Missing fields. Please provide username, password, and access token."
                }), 400

            # Validate user credentials
            user = User.query.filter_by(username=data['username']).first()
            if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), base64.b64decode(user.password)):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid credentials. The provided username or password is incorrect."
                }), 401

            # Validate the access token
            try:
                decoded_token = decode_token(data['access_token'])  # Verify JWT format
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "code": "INVALID_TOKEN",
                    "message": "Invalid access token provided."
                }), 401

            # Store user and token in session
            #The access token is stored in the session, so that routes such as store, retireve, update and delete can be accessed
            session['user_id'] = user.id
            session['username'] = user.username
            session['access_token'] = data['access_token']

            # Redirect to the dashboard after successful login
            return redirect(url_for('dashboard'))

        except Exception as e:
            app.logger.error(f"Error occurred while logging in: {str(e)}")
            return jsonify({
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": "Internal server error occurred. Please try again later."
            }), 500

    
    return render_template("login.html")


#Route for Dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        # Check if access token exists in session
        if 'access_token' not in session:
            return redirect(url_for('login'))

        # Use token for Authorization header
        access_token = session['access_token']
        decoded_token = decode_token(access_token)  # Decode and validate token

        # Fetch user details
        current_user_id = decoded_token['sub']
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404

        return render_template('dashboard.html', user=user)

    except Exception as e:
        app.logger.error(f"Error occurred while accessing dashboard: {str(e)}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": "Internal server error occurred. Please try again later."
        }), 500


#Route for storing data
@app.route("/api/data", methods=["POST", "GET"])
def store_data():
    try:
        # Check if user is authenticated
        if 'access_token' not in session:
            return redirect(url_for('login'))

        #The access token is optained form the session
        # Decode and validate the access token
        access_token = session['access_token']
        try:
            decoded_token = decode_token(access_token)
            current_user_id = decoded_token['sub']
        except Exception as e:
            print(f"Token decoding error: {str(e)}")
            return jsonify({
                "status": "error",
                "code": "INVALID_TOKEN",
                "message": "Invalid access token provided."
            }), 401

        # Fetch the user details
        user = User.query.get(current_user_id)

        if request.method == "POST":
            # Retrieve form data
            data = request.form.to_dict()

            # Validate input
            if 'key' not in data or not data['key'].strip():
                return jsonify({
                    "status": "error",
                    "code": "INVALID_KEY",
                    "message": "The provided key is not valid or missing."
                }), 400

            if 'value' not in data or not data['value'].strip():
                return jsonify({
                    "status": "error",
                    "code": "INVALID_VALUE",
                    "message": "The provided value is not valid or missing."
                }), 400

            key = data['key'].strip()
            value = data['value'].strip()

            # Check if the key already exists
            existing_data = Data.query.filter_by(user_id=current_user_id, key=key).first()
            if existing_data:
                return jsonify({
                    "status": "error",
                    "code": "KEY_EXISTS",
                    "message": "The provided key already exists in the database. To update an existing key, use the update API."
                }), 409

            # Store new data
            new_data = Data(user_id=current_user_id, key=key, value=value)
            db.session.add(new_data)
            db.session.commit()

            # Success response
            message = {
                "status": "success",
                "message": "Data stored successfully."
            }
            return render_template("store_data.html", message=message)

        # Render the form for GET requests
        return render_template("store_data.html", message=None)

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred."
        }), 500


#Route for retrieving data
@app.route("/api/data/retrieve", methods=["GET"])
def retrieve_data():
    try:
        # Ensure the user is logged in
        if 'access_token' not in session:
            return redirect(url_for('login'))
        
        # Extract the key from query parameters
        key = request.args.get('key') 
        if not key:
            message = {
                "status": "error",
                "message": "Key is required to retrieve data."
            }
            return render_template("retrieve_data.html", message=message)
        # The access token is optained form the session
        # Decode the access token to get the user ID
        access_token = session['access_token']
        try:
            decoded_token = decode_token(access_token)
            current_user_id = decoded_token['sub']
        except Exception as e:
            message = {
                "status": "error",
                "code" : "INVALID_TOKEN",
                "message": "Invalid access token. Please log in again."
            }
            return render_template("retrieve_data.html", message=message)

        # Query the database for the key
        existing_data = Data.query.filter_by(user_id=current_user_id, key=key).first()
        if not existing_data:
            message = {
                "status": "error",
                "code" : "KEY_NOT_FOUND",
                "message" : "The provided key does not exist in the database."
            }
            return render_template("retrieve_data.html", message=message)

        # Return success with the retrieved data
        message = {
            "status": "success",
            "message": "Data retrieved successfully!",
            "data": {
                "key": existing_data.key,
                "value": existing_data.value
            }
        }
        return render_template("retrieve_data.html", message=message)

    except Exception as e:
        # Catch any other unexpected exceptions
        message = {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }
        return render_template("retrieve_data.html", message=message)


#Route for updating data
@app.route("/api/data/update", methods=['POST', 'GET'])
def update_data():
    try:
        if 'access_token' not in session:
            return redirect(url_for('login'))

        if request.method == "POST":
            # Extract key and value from the form data
            key = request.form.get('key')
            value = request.form.get('value')
            access_token = session['access_token']

            try:
                # Decode the access token to get the user ID
                decoded_token = decode_token(access_token)
                current_user_id = decoded_token['sub']
            except Exception as e:
                # Handle invalid access token
                print(f"Token decoding error: {str(e)}")
                message = {
                    "status": "error",
                    "message": "Invalid access token provided.",
                    "code": "INVALID_TOKEN"
                }
                return render_template("update_data.html", message=message)

            # Check if the provided key exists for the current user
            existing_data = Data.query.filter_by(user_id=current_user_id, key=key).first()
            if not existing_data:
                message = {
                    "status": "error",
                    "message": "The provided key does not exist in the database.",
                    "code": "KEY_NOT_FOUND"
                }
                return render_template("update_data.html", message=message)

            # Update the value
            if not value:
                message = {
                    "status": "error",
                    "message": "New value is required to update the data."
                }
                return render_template("update_data.html", message=message)

            existing_data.value = value
            db.session.commit()

            # Success message
            message = {
                "status": "success",
                "message": "Data updated successfully."
            }
            return render_template("update_data.html", message=message)

        # Render the form for GET requests
        return render_template("update_data.html", message=None)

    except Exception as e:
        # Log the error for debugging
        print(f"Unexpected error occurred: {str(e)}")
        message = {
            "status": "error",
            "message": "An unexpected error occurred."
        }
        return render_template("update_data.html", message=message)


#Route for deleting data
@app.route('/api/data/delete', methods=['GET', 'POST'])
def delete_data():
    try:
        # Check if the user is logged in
        if 'access_token' not in session:
            return redirect(url_for('login'))

        if request.method == "POST":
            key = request.form.get('key')  # Get the key from the form
            access_token = session['access_token']

            # Decode the access token
            try:
                decoded_token = decode_token(access_token)
                current_user_id = decoded_token['sub']
            except Exception as e:
                print(f"Token decoding error: {str(e)}")
                message = {
                    "status": "error",
                    "code": "INVALID_TOKEN",
                    "message": "Invalid access token provided."
                }
                return render_template("delete_data.html", message=message)

            # Check if the key exists in the database
            data = Data.query.filter_by(user_id=current_user_id, key=key).first()
            if not data:
                message = {
                    "status": "error",
                    "code": "KEY_NOT_FOUND",
                    "message": "The provided key does not exist in the database."
                }
                return render_template("delete_data.html", message=message)

            # Delete the data entry
            db.session.delete(data)
            db.session.commit()

            # Return a success message
            message = {
                "status": "success",
                "message": "Data deleted successfully."
            }
            return render_template("delete_data.html", message=message)

        # Render the form for GET requests
        return render_template("delete_data.html", message=None)

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        message = {
            "status": "error",
            "message": "An unexpected error occurred."
        }
        return render_template("delete_data.html", message=message)



#Route for logging out
@app.route("/api/logout")
def logout():
    try:
        # Clear the session to log out the user
        session.clear()
        
        # Redirect to login page after logging out
        return redirect(url_for("login"))
    except Exception as e:
        # Log the exception if any error occurs
        app.logger.error(f"Error occurred during logout: {str(e)}")
        
        return jsonify({
            "status": "error",
            "message": "An error occurred during logout. Please try again later."
        }), 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
