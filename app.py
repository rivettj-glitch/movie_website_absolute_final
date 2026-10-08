from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()
    sql = """
        SELECT movie_name, release_year, length, age_rating, cost
        FROM movies
        WHERE bestseller = 1"""
    cursor.execute(sql)
    movies = cursor.fetchall()
    db.close()
    return render_template("index.html", movies=movies)

@app.route("/movies")
def movies():
    return "<h1>Movies Page</h1>"

@app.route("/favourites")
def favourites():
    return "<h1>Favourites Page</h1>"

@app.route("/about")
def about():
    return "<h1>About Page</h1>"

if __name__ == "__main__":
    app.run(debug=True)