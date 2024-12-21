# Key-Value Store API with Flask



## 📋 Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Security Features](#security-features)

## ✨ Features
- User registration and authentication
- JWT-based session management
- Secure password hashing using bcrypt
- CRUD operations for key-value pairs
- User-specific data isolation
- Web interface for all operations
- Docker support for easy deployment

## 🛠 Technology Stack

### Core Framework
- **Flask**: Chosen for its lightweight nature, flexibility, and extensive ecosystem. Flask's minimalist approach allows for precise control over the application architecture while maintaining simplicity.

### Database
- **SQLite**: Used with SQLAlchemy ORM for:
  - Development simplicity
  - Zero-configuration database
  - File-based storage
  - Perfect for prototypes and small to medium applications

### Security
- **Flask-JWT-Extended**: Handles JWT token generation and validation
- **Bcrypt**: Industry-standard password hashing
- **Werkzeug**: Security utilities and password hashing verification

### Frontend
- **HTML/CSS**: Simple and responsive web interface
- **Jinja2**: Flask's default templating engine

### Development & Deployment
- **Docker**: Containerization for consistent development and deployment
- **Docker Compose**: Multi-container application orchestration



## 🗄 Database Schema

### User Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL
);
```


### Data Table (Key-Value Store)
```sql
CREATE TABLE data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key VARCHAR(100) UNIQUE NOT NULL,
    value VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```



## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/register` | POST | User registration |
| `/api/token` | POST | Generate access token |
| `/api/login` | POST | User login |
| `/api/data` | POST | Store key-value pair |
| `/api/data/retrieve` | GET | Retrieve value by key |
| `/api/data/update` | POST | Update existing value |
| `/api/data/delete` | POST | Delete key-value pair |
| `/api/logout` | GET | User logout |



## 📁 Project Structure
```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── src/
    ├── app.py                 # Main application file
    ├── instance/             # SQLite database directory
    ├── static/               # CSS files
    │   ├── delete_data.css
    │   ├── generate_token.css
    │   ├── login.css
    │   ├── register.css
    │   ├── retrieve_data.css
    │   ├── store_data.css
    │   └── update_data.css
    └── templates/            # HTML templates
        ├── dashboard.html
        ├── delete_data.html
        ├── generate_token.html
        ├── layout.html
        ├── login.html
        ├── register.html
        ├── retrieve_data.html
        ├── store_data.html
        └── update_data.html
```

## 🚀 Setup and Installation



### Prerequisites
- Docker and Docker Compose installed [Make is optional]
- Git (optional)

### Local Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a `.env` file (optional):
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application at `http://localhost:5000`

### Manual Setup (Without Docker)
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   cd src
   python app.py
   ```

## 🔧 Running the Application

### Using Docker
```bash
# Start the application
docker-compose up

# Stop the application
docker-compose down

# View logs
docker-compose logs -f
```

### Manual Run
```bash
# From the src directory
python app.py
```
### Using Make and Docker
```bash
   #  build the application
   make build
   # run the application
   make run
   # stop the application
   make stop
   # remove the container
   make remove
   # remove the image
   make removei

```

## 🔒 Security Features
- Password hashing using bcrypt
- JWT-based authentication
- Session management
- CSRF protection
- Input validation
- Secure password requirements:
  - Minimum 8 characters
  - Must contain uppercase and lowercase letters
  - Must contain numbers
  - Must contain special characters

## 🧪 Testing
Run the tests using:
```bash
#This is to be runned if the server is running
python -m pytest test.py

#Or 

python3 test.py
```




