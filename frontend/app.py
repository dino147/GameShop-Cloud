from flask import Flask, request, redirect, url_for, render_template, jsonify
import jwt
import os
import requests
from functools import wraps
import logging

SECRET_KEY = "Aidwj3iijsjFew12esjdiaPRasecret"
auth_url = os.getenv("AUTH_URL", default="http://localhost:5001")
games_url = os.getenv("GAMES_URL", default="http://localhost:5002")
reviews_url = os.getenv("REVIEWS_URL", default="http://localhost:5003")
library_url = os.getenv("LIBRARY_URL", default="http://localhost:5004")

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Pornire aplicatie debug')

# Decorator for login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect(url_for("login_page"))

        try:
            jwt.decode(token, SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login_page"))
        except jwt.InvalidTokenError:
            return redirect(url_for("login_page"))

        return f(*args, **kwargs)

    return decorated_function

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        response = requests.post(f"{auth_url}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json()["token"]
            resp = redirect(url_for("home"))
            resp.set_cookie("token", token)
            return resp

        return "Invalid credentials", 401

    return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        response = requests.post(f"{auth_url}/register", json={"username": username, "password": password, "first_name": first_name, "last_name":last_name})
        if response.status_code == 200:
            token = response.json()["token"]
            resp = redirect(url_for("home"))
            resp.set_cookie("token", token)
            return resp

        return "Username and password required", 401

    return render_template("register.html")

@app.route("/games", methods=["GET", "POST"])
@login_required
def manage_games():
    if request.method == "POST":
        app.logger.debug("Frontend Game add request: %s", request.form)
        name = request.form["name"]
        genre = request.form["genre"]
        company = request.form["company"]
        launch_date = request.form["launch_date"]
        price = request.form["price"]
        requests.post(f"{games_url}/games", json={"name": name, "genre": genre, "company": company, "launch_date": launch_date, "price": price})
        return redirect(url_for("manage_games"))
        
    response = requests.get(f"{games_url}/games")
    games = response.json()
    return render_template("games.html", games=games)

@app.route("/reviews", methods=["GET", "POST"])
@login_required
def manage_reviews():
    if request.method == "POST":
        review = request.form["review"]
        game_id = request.form["game_id"]
        rating = request.form["rating"]
        user = jwt.decode(request.cookies.get("token"), SECRET_KEY, algorithms="HS256")["username"]
        requests.post(f"{reviews_url}/reviews", json={"review": review, "game_id": game_id, "username": user, "rating": rating })
        return redirect(url_for("manage_reviews"))

    response = requests.get(f"{reviews_url}/reviews")
    reviews = response.json()
    
    for review in reviews:
        game_id = review["game_id"]
        game_response = requests.get(f"{games_url}/game/{game_id}") 
        if game_response.status_code == 200:
            game_data = game_response.json()
            app.logger.debug("Frontend get game with id: " + str(game_id) + " response " + str(game_data))
            review["game_name"] = game_data.get("name", "Unknown Game")
        else:
            app.logger.error("Failed to fetch game with id: " + str(game_id) + " status code: " + str(game_response.status_code))
            review["game_name"] = "Unknown Game"
    
    return render_template("reviews.html", reviews=reviews)
    
    
@app.route("/library", methods=["GET", "POST"])
@login_required
def manage_library():
    if request.method == "POST":
        app.logger.debug("Frontend Library add request: %s", request.form)
       
        game_id = request.form["game_id"]
        username = jwt.decode(request.cookies.get("token"), SECRET_KEY, algorithms="HS256")["username"]
        downloaded = request.form["downloaded"].lower() == "true"
        dlc = request.form["dlc"].lower() == "true"
        
        requests.post(f"{library_url}/library", json={
            "game_id": game_id,
            "username": username,
            "downloaded": downloaded,
            "dlc": dlc
        })
        return redirect(url_for("manage_library"))
    
    user = jwt.decode(request.cookies.get("token"), SECRET_KEY, algorithms="HS256")["username"]
    response = requests.get(f"{library_url}/library", params={"user": user})
    library_games = response.json()
    
    for lib_game in library_games:
        game_id = lib_game["game_id"]
        game_response = requests.get(f"{games_url}/game/{game_id}") 
        if game_response.status_code == 200:
            game_data = game_response.json()
            app.logger.debug("Frontend get game with id: " + str(game_id) + " response " + str(game_data))
            lib_game["game_name"] = game_data.get("name", "Unknown Game")
        else:
            app.logger.error("Failed to fetch game with id: " + str(game_id) + " status code: " + str(game_response.status_code))
            lib_game["game_name"] = "Unknown Game"

    return render_template("library.html", library_games=library_games)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
