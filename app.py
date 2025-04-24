from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

# Initialize the app
app = Flask(__name__)

# Configure the app (example configurations)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)  # Enable Cross-Origin Resource Sharing
bcrypt = Bcrypt(app)  # Password hashing
db = SQLAlchemy(app)  # Database instance
jwt = JWTManager(app)  # JWT instance

# Define models (example User model)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Example route to register a user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(message="User registered successfully"), 201

# Example route to login and get a JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    
    return jsonify(message="Invalid credentials"), 401

# Example protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message=f"Welcome, user {current_user}"), 200

# Example route to get the current server time
@app.route('/time', methods=['GET'])
def get_time():
    now = datetime.datetime.now()
    return jsonify(current_time=now.strftime('%Y-%m-%d %H:%M:%S')), 200

if __name__ == "__main__":
    app.run(debug=True)
