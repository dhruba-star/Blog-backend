from flask import Flask, request, jsonify from flask_cors import CORS from flask_bcrypt import Bcrypt from flask_sqlalchemy import SQLAlchemy from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity import datetime

app = Flask(name) CORS(app) app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db' app.config['SECRET_KEY'] = 'your_secret_key' app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app) bcrypt = Bcrypt(app) jwt = JWTManager(app)

Models

class User(db.Model): id = db.Column(db.Integer, primary_key=True) username = db.Column(db.String(150), unique=True, nullable=False) password = db.Column(db.String(200), nullable=False)

class Blog(db.Model): id = db.Column(db.Integer, primary_key=True) title = db.Column(db.String(200), nullable=False) content = db.Column(db.Text, nullable=False) date = db.Column(db.String(50), nullable=False) author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

Routes

@app.route('/api/register', methods=['POST']) def register(): data = request.json if User.query.filter_by(username=data['username']).first(): return jsonify({"message": "User already exists"}), 409 hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8') new_user = User(username=data['username'], password=hashed_pw) db.session.add(new_user) db.session.commit() return jsonify({"message": "User created"}), 201

@app.route('/api/login', methods=['POST']) def login(): data = request.json user = User.query.filter_by(username=data['username']).first() if user and bcrypt.check_password_hash(user.password, data['password']): token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(hours=2)) return jsonify({"token": token}), 200 return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/blog', methods=['POST']) @jwt_required() def create_blog(): data = request.json user_id = get_jwt_identity() new_blog = Blog(title=data['title'], content=data['content'], date=data['date'], author_id=user_id) db.session.add(new_blog) db.session.commit() return jsonify({"message": "Blog posted"}), 201

@app.route('/api/blogs', methods=['GET']) def get_blogs(): blogs = Blog.query.order_by(Blog.id.desc()).all() return jsonify([{"id": b.id, "title": b.title, "date": b.date} for b in blogs])

@app.route('/api/blog/int:id', methods=['GET']) def get_blog(id): blog = Blog.query.get_or_404(id) return jsonify({"title": blog.title, "content": blog.content, "date": blog.date})

if name == 'main': with app.app_context(): db.create_all() app.run(debug=True)

