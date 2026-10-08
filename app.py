from flask import Flask, render_template, Response
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()
    sql = """
        SELECT movie_id, movie_name, release_year, length, age_rating, cost
        FROM movies
        WHERE bestseller = 1"""
    cursor.execute(sql)
    best_sellers = cursor.fetchall()
    db.close()
    return render_template("index.html", best_sellers=best_sellers)

@app.route("/favourites")
def favourites():
    return "<h1>Favourites Page</h1>"

@app.route("/about")
def about():
    return "<h1>About Page</h1>"

@app.route("/poster/<int:movie_id>")
def poster(movie_id):
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()
    sql = f"""
        SELECT poster 
        FROM movies
        WHERE movie_id = {movie_id}"""
    cursor.execute(sql)
    poster_data = cursor.fetchone()
    db.close()
    return Response(poster_data[0], mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(debug=True)