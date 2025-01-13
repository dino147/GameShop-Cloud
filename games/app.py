from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, Numeric, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Pornire aplicatie debug')

engine = create_engine('postgresql://postgres:game-pw@postgres2:5432/game-db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

session = Session()

class Game(Base):
    __tablename__ = 'games'
    id=Column(Integer, primary_key=True)
    name=Column('name', String(32))
    genre=Column('genre', String(32))
    company=Column('company', String(32))
    launch_date=Column('launch_date', Date)
    price=Column('price', Numeric)
    
    def __init__(self, name, genre, company, launch_date, price):
        self.name = name
        self.genre = genre
        self.company = company
        self.launch_date = launch_date
        self.price = price
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "genre": self.genre,
            "company": self.company,
            "launch_date": self.launch_date.isoformat() if self.launch_date else None,
            "price": float(self.price) if self.price else None
        }
        
# generate database schema
Base.metadata.create_all(engine)

if session.query(Game).filter(Game.name == "Minecraft").first() is None:
    game = Game("Minecraft", "creative", "Mojang inc.", datetime.strptime("2012-05-06", "%Y-%m-%d").date(), 30.0)
    
    session.add(game)
    session.commit()

    app.logger.debug(f"Game added: {game.name}, {game.genre}, {game.company}, {game.launch_date}, {game.price}")


@app.route("/games", methods=["GET"])
def get_games():
    games = session.query(Game).all()
    games_dict = [game.to_dict() for game in games]
    return jsonify(games_dict)
    
@app.route("/game/<int:game_id>", methods=["GET"])
def get_game(game_id):
    app.logger.debug("Get game with id: " + str(game_id))
    game = session.query(Game).filter(Game.id == game_id).first()
    if game is None:
        return jsonify({"error": "Game not found!"}), 404
    game_dict = game.to_dict()
    return jsonify(game_dict)

@app.route("/games", methods=["POST"])
def add_game():
    app.logger.debug("Game add request")
    data = request.json
    game = Game(data["name"], data["genre"], data["company"], datetime.strptime(data["launch_date"], "%Y-%m-%d"), float(data["price"]))
    session.add(game)
    session.commit()
    return jsonify({"message": "Game added successfully"})

session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)