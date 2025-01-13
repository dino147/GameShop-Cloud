from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, Numeric, String, Float, Boolean, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug('Pornire aplicatie debug')

engine = create_engine('postgresql://postgres:reviews-pw@postgres3:5432/reviews-db')
Session = sessionmaker(bind=engine)

Base = declarative_base()

session = Session()

#Base.metadata.drop_all(engine)

class Review(Base):
    __tablename__ = 'reviews'
    id=Column(Integer, primary_key=True)
    game_id=Column('game_id', Integer)
    username=Column('username', String(32))
    rating=Column('rating', Integer)
    review=Column('review', String(120))
    submit_date=Column('submit_date', Date)

    def __init__(self, game_id, username, rating, review, submit_date):
        self.game_id = game_id
        self.username = username
        self.rating = rating
        self.review = review
        self.submit_date = submit_date
        
    def to_dict(self):
        return {
            "id": self.id,
            "game_id": self.game_id,
            "username": self.username,
            "rating": self.rating,
            "review": self.review,
            "submit_date": self.submit_date.isoformat() if self.submit_date else None,
        }
        
# generate database schema
Base.metadata.create_all(engine)

@app.route("/reviews", methods=["GET"])
def get_reviews():
    reviews = session.query(Review).all()
    reviews_dict = [review.to_dict() for review in reviews]
    return jsonify(reviews_dict)

@app.route("/reviews", methods=["POST"])
def add_review():
    app.logger.debug("Review add request")
    data = request.json
    review = Review(int(data["game_id"]), data["username"], data["rating"], data["review"], datetime.now())
    session.add(review)
    session.commit()
    return jsonify({"message": "Review added successfully"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
