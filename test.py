import requests
import random

url = "http://localhost:5000"

# Generate unique user data
user_name = "test_user_{0}".format(random.randint(1, int(1e6)))
email = "{0}@example.com".format(user_name)
key_name = "test_key_{0}".format(random.randint(1, 1e6))

def test_register_user_success():
    endpoint = "/api/register"
    data = {
        "username": user_name,
        "email": email,
        "password": "Test@password123",
        "full_name": "Test User",
        "age": 30,
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["message"] == "User successfully registered!"

def test_register_user_missing_fields():
    endpoint = "/api/register"
    data = {
        "username": user_name,  # Missing email, password, etc.
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"

def test_register_user_existing_email():
    endpoint = "/api/register"
    data = {
        "username": "new_user_{0}".format(random.randint(1, int(1e6))),
        "email": email,  # Reusing the same email
        "password": "Test@password123",
        "full_name": "Test User",
        "age": 30,
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_EXISTS"

def test_register_user_invalid_password():
    endpoint = "/api/register"
    data = {
        "username": "weakpass_user_{0}".format(random.randint(1, int(1e6))),
        "email": "weakpass@example.com",
        "password": "weak",  # Invalid password
        "full_name": "Test User",
        "age": 30,
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_PASSWORD"

def test_register_user_invalid_age():
    endpoint = "/api/register"
    data = {
        "username": "invalidage_user_{0}".format(random.randint(1, int(1e6))),
        "email": "invalidage@example.com",
        "password": "Test@password123",
        "full_name": "Test User",
        "age": -5,  # Invalid age
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_AGE"

def test_register_user_blank_gender():
    endpoint = "/api/register"
    data = {
        "username": "blankgender_user_{0}".format(random.randint(1, int(1e6))),
        "email": "blankgender@example.com",
        "password": "Test@password123",
        "full_name": "Test User",
        "age": 30,
        "gender": ""  # Blank gender
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 400
    assert response.json()["code"] == "GENDER_REQUIRED"

def test_register_user_existing_username():
    endpoint = "/api/register"
    data = {
        "username": user_name,  # Reusing the same username
        "email": "unique_email_{0}@example.com".format(random.randint(1, int(1e6))),
        "password": "Test@password123",
        "full_name": "Test User",
        "age": 30,
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 409
    assert response.json()["code"] == "USERNAME_EXISTS"

username = "test_user_{0}".format(random.randint(1, int(1e6)))
password = "Test@password123"

# Helper function to register a user for testing
def register_user():
    endpoint = "/api/register"
    data = {
        "username": username,
        "email": "{0}@example.com".format(username),
        "password": password,
        "full_name": "Test User",
        "age": 30,
        "gender": "male"
    }
    response = requests.post(url + endpoint, json=data)
    if response.status_code != 200:
        print("Failed to register user. Response:", response.status_code, response.text)



def test_generate_token_success():
    endpoint = "/api/token"
    data = {
        "username": username,
        "password": password
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "access_token" in response.json()["data"]
    return {"Authorization": "Bearer {0}".format(response.json()['data']['access_token'])}


def test_generate_token_missing_fields():
    endpoint = "/api/token"
    data = {
        "username": username  # Missing password
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 400
    assert response.json()["code"] == "MISSING_FIELDS"

def test_generate_token_invalid_credentials():
    endpoint = "/api/token"
    data = {
        "username": username,
        "password": "WrongPassword123"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"

def test_generate_token_nonexistent_user():
    endpoint = "/api/token"
    data = {
        "username": "nonexistent_user_{0}".format(random.randint(1, int(1e6))),
        "password": "Test@password123"
    }
    response = requests.post(url + endpoint, json=data)
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"

def test_generate_token_internal_error():

    endpoint = "/api/token"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url + endpoint, data="corrupt_payload") 
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"


def test_store_data():
    endpoint = "/api/data"
    data = {
        "key": key_name,
        "value": "test_value"
    }
    response = requests.post(url + endpoint, json=data, headers=test_generate_token_success())
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["message"] == "Data stored successfully."

def test_retrieve_data():
    endpoint = "/api/data/{0}".format(key_name)
    response = requests.get(url + endpoint, headers=test_generate_token_success())
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["data"]["key"] == key_name
    assert response.json()["data"]["value"] == "test_value"

def test_update_data():
    endpoint = "/api/data/{0}".format(key_name)
    data = {
        "value": "new_test_value"
    }
    response = requests.put(url + endpoint, json=data, headers=test_generate_token_success())
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["message"] == "Data updated successfully."

def test_delete_data():
    endpoint = "/api/data/{0}".format(key_name)
    response = requests.delete(url + endpoint, headers=test_generate_token_success())
    print("response", response.request.url, response.request.method, response.status_code, response.text)
    assert response.status_code == 200
    assert response.json()["message"] == "Data deleted successfully."


def test_all_register_cases():
    test_register_user_success()
    test_register_user_missing_fields()
    test_register_user_existing_email()
    test_register_user_invalid_password()
    test_register_user_invalid_age()
    test_register_user_blank_gender()
    test_register_user_existing_username()
    register_user()  
    test_generate_token_success()
    test_generate_token_missing_fields()
    test_generate_token_invalid_credentials()
    test_generate_token_nonexistent_user()
    test_generate_token_internal_error()
    
    test_store_data()
    test_retrieve_data()
    test_update_data()
    test_delete_data()

if __name__ == "__main__":
    test_all_register_cases()
