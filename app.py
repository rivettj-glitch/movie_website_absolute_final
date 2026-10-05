from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()
    sql = """
        SELECT movie_id, movie_name, release_year, length, age_rating, cost, bestseller
        FROM movies"""
    cursor.execute(sql)
    movies = cursor.fetchall()
    db.close()
    return render_template("index.html", movies=movies)

if __name__ == "__main__":
    app.run(debug=True)