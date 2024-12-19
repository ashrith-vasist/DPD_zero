from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import base64

app = Flask(__name__)


# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key_here"



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


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(100), nullable=False)
    user = db.relationship('User', back_populates="data")


User.data = db.relationship('Data', back_populates="user")

@app.route("/api/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            data = request.get_json()

            required_fields = ("username", "email", "password", "full_name", "age", "gender")
            #INVALID_REQUEST
            if not all(key in data for key in required_fields):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": "Invalid request. Please provide all required fields: username, email, password, full_name, age, gender."
                }), 400

            #USERNAME_EXISTS
            if User.query.filter_by(username=data['username']).first():
                return jsonify({
                    "status": "error",
                    "code": "USERNAME_EXISTS",
                    "message": "The provided username is already taken. Please choose a different username."
                }), 409
            
            #EMAIL_EXISTS
            if User.query.filter_by(email=data['email']).first():
                return jsonify({
                    "status": "error",
                    "code": "EMAIL_EXISTS",
                    "message": "The provided email is already registered. Please use a different email address."
                }), 409
            
            #INVALID_PASSWORD
            if len(data['password']) < 8 or not re.search(r'[A-Z]', data['password']) or \
            not re.search(r'[a-z]', data['password']) or not re.search(r'\d', data['password']) or \
            not re.search(r'[!@#$%^&*(),.?":{}|<>]', data['password']):
                return jsonify({
                    "status": "error",
                    "code": "INVALID_PASSWORD",
                    "message": "Password must be at least 8 characters long and contain an uppercase letter, lowercase letter, number, and special character."
                }), 400

            #INVALID_AGE
        
            if not data['age'] or int(data['age']) <= 0:
                return jsonify({
                    "status": "error",
                    "code": "INVALID_AGE",
                    "message": "Invalid age value. Age must be a positive integer."
                }), 400
            
            #GENDER_REQUIRED
            if not data['gender'].strip():
                return jsonify({
                    "status": "error",
                    "code": "GENDER_REQUIRED",
                    "message": "Gender field is required. Please specify the gender."
                }), 400
            
            # Hash the password
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = base64.b64encode(hashed_password).decode('utf-8')

            # Create new user
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

            return jsonify({
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
            }), 200
        
        except:
            return jsonify({
                "status" : "error",
                "code" : "INTERNAL_SERVER_ERROR",
                "message" : "An internal server error occurred. Please try again later."
            }), 500


    

@app.route("/api/token", methods=["POST", "GET"])
def generate_token():
    if request.method == "POST":
        try:
            data = request.get_json()

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
            return jsonify({
                "status": "success",
                "message": "Access token generated successfully.",
                "data": {
                    "access_token": access_token,
                    "expires_in": 3600
                }
            }), 200
        
        except:
            return jsonify({
                "status" : "error",
                "code" : "INTERNAL_ERROR",
                "message" : "Internal server error occurred. Please try again later."                
            }), 500
            
        



### PASS A CURL COMMAND TO EXECUTE THIS
@app.route("/api/data", methods=["POST", "GET"])
@jwt_required()
def store_data():
    current_user_id = get_jwt_identity()
    
    if request.method == "POST":
        data = request.get_json()  # Correctly accessing form data
        print("hello")
        print(data)
        if not data :
            return jsonify({
                "status": "error",
                "code": "Empty message",
                "message": "The provided value or key is not valid or missing"
            }), 400
        
        key = data['key'].strip()
        value = data['value'].strip()

        existing_data = Data.query.filter_by(user_id=current_user_id, key=key).first()
        if existing_data:
            return jsonify({
                "status": "error",
                "code": "KEY_EXISTS",
                "message": "The provided key already exists in the database. To update an existing key, use the update API."
            }), 409
        
        new_data = Data(user_id=current_user_id, key=key, value=value)  # Corrected: user = value
        db.session.add(new_data)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Data stored successfully."
        }), 200
    
    return render_template("store_data.html")


@app.route("/api/data/<key>", methods = ["GET"])
@jwt_required()
def retrieve_data(key):
    try:
        currnet_user_id = get_jwt_identity()
        
        existing_data = Data.query.filter_by(user_id = currnet_user_id, key = key).first()
        if not existing_data:
            return jsonify({
                "status" : "error",
                "code" : "KEY_NOT_FOUND",
                "message" : "The provided key does not exist in the database."
            }), 404
        
        return jsonify({
            "status" : "success",
            "data" : {
                "key" : existing_data.key,
                "value" : existing_data.value
            }})    
    except:
        return jsonify({
            "status": "error",
            "code": "INVALID_TOKEN",
            "message": "Invalid access token provided."
        }), 401 

@app.route("/api/data/<key>", methods=["PUT"])
@jwt_required()
def update_data(key):
    try:
        # Get the current user ID from the JWT token
        current_user_id = get_jwt_identity()
        
        # Get the data from the request body
        data = request.get_json()

        # Check if the provided key exists for the current user
        existing_data = Data.query.filter_by(user_id=current_user_id, key=key).first()
        if not existing_data:
            return jsonify({
                "status": "error",
                "code": "KEY_NOT_FOUND",
                "message": "The provided key does not exist in the database."
            }), 404

        # Update the value of the existing data
        if 'value' not in data:
            return jsonify({
                "status": "error",
                "code": "MISSING_VALUE",
                "message": "'value' key is missing in the request."
            }), 400
        
        existing_data.value = data['value']
        db.session.commit()

        # Return a success message
        return jsonify({
            "status": "success",
            "message": "Data updated successfully."
        }), 200

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "code": "INVALID_TOKEN",
            "message": "Invalid access token provided."
        }), 401

@app.route('/api/data/<key>', methods=['DELETE'])
@jwt_required()
def delete_data(key):
    try:
        current_user_id = get_jwt_identity()

        # Find the data entry by user_id and key
        data = Data.query.filter_by(user_id=current_user_id, key=key).first()

        # Return an error if the key is not found
        if not data:
            return jsonify({
                "status": "error",
                "code": "KEY_NOT_FOUND",
                "message": "The provided key does not exist in the database."
            }), 404

        # Delete the data entry and commit the change
        db.session.delete(data)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Data deleted successfully."
        }), 200

    except:
        # Handle any JWT or server-related errors
        return jsonify({
            "status": "error",
            "code": "INVALID_TOKEN",
            "message": "Invalid access token provided."
        }), 401




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
