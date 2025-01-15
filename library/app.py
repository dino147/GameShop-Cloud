from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, Numeric, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging
import time
import psycopg2

def wait_for_db():
    while True:
        try:
            conn = psycopg2.connect(
                host="postgres4",
                database="library-db",
                user="postgres",
                password="library-pw"
            )
            conn.close()
            break
        except Exception as e:
            print("Database not ready, retrying in 5 seconds...")
            time.sleep(5)

wait_for_db()

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Pornire aplicatie debug')

engine = create_engine('postgresql://postgres:library-pw@postgres4:5432/library-db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

session = Session()

class LibraryGame(Base):
    __tablename__ = 'library-game'
    id=Column(Integer, primary_key=True)
    game_id=Column('game_id', Integer)
    username=Column('username', String(32))
    purchase_date=Column('purchase_date', Date)
    downloaded=Column('downloaded', Boolean)
    dlc=Column('dlc', Boolean)

    def __init__(self, game_id, username, purchase_date, downloaded, dlc):
        self.game_id = game_id
        self.username = username
        self.purchase_date = purchase_date
        self.downloaded = downloaded
        self.dlc = dlc
        
    def to_dict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "username": self.username,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "downloaded": self.downloaded,
            "dlc": self.dlc,
        }
        
# generate database schema
Base.metadata.create_all(engine)

@app.route("/library", methods=["GET"])
def get_orders():
    user = request.args.get("user")
    library_games = session.query(LibraryGame).all()
    user_games = [lib_game.to_dict() for lib_game in library_games if lib_game.username == user]
    return jsonify(user_games)

@app.route("/library", methods=["POST"])
def add_order():
    app.logger.debug("Library Game add request")
    data = request.json
    user = request.args.get("user")
    lib_game = LibraryGame(int(data["game_id"]), data["username"], datetime.now(), data["downloaded"], data["dlc"])
    session.add(lib_game)
    session.commit()
    return jsonify({"message": "Order placed successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
