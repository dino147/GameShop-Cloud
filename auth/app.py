from flask import Flask, request, jsonify
import jwt
import datetime
from sqlalchemy import create_engine, Column, Integer, Numeric, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib
import bcrypt
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Pornire aplicatie debug')
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

engine = create_engine('postgresql://postgres:my-secret-pw@postgres:5432/auth-db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

session = Session()

class User(Base):
    __tablename__ = 'user'
    id=Column(Integer, primary_key=True)
    username=Column('username', String(32))
    pwd_hash=Column('password', String(64))
    first_name=Column('first_name', String(32))
    last_name=Column('last_name', String(32))
# 2 - generate database schema
Base.metadata.create_all(engine)

SECRET_KEY = "Aidwj3iijsjFew12esjdiaPRasecret"

app.logger.debug("User admin" + session.query(User).filter(User.username == "admin").first().pwd_hash)
# Query the user to be deleted
user_to_delete = session.query(User).filter(User.username == 'admin').first()

# Check if the user exists and delete
if user_to_delete:
    session.delete(user_to_delete)
    session.commit()
    print("User deleted")
else:
    print("User not found")

if session.query(User).filter(User.username == "admin").first() is None:
    u = User()
    u.username = "admin"
    u.pwd_hash = bcrypt.hashpw("pass".encode(), bcrypt.gensalt()).decode()
    u.first_name = "John"
    u.last_name = "Keller"
    app.logger.debug("Hash parola creata:" + u.pwd_hash)

    session.add(u)
    session.commit()

#app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = session.query(User).filter(User.username == username).first()

    if user and bcrypt.checkpw(password.encode(), user.pwd_hash.encode()):
        token = jwt.encode({"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    else:
        return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

