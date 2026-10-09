from flask import Flask, render_template, Response, request
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

@app.route("/movies")
def movies():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()

    search = request.args.get("search")
    sort = request.args.get("sort")

    sql = """
        SELECT movie_id, movie_name, release_year, length, age_rating, cost
        FROM movies"""
    filters= ()
    if search:
        sql += " WHERE movie_name LIKE ?"
        filters = ("%" + search + "%",)

    sort_options = [("price_asc", "cost ASC"), 
                    ("price_desc", "cost DESC"),
                    ("name_asc", "movie_name ASC"),
                    ("name_desc", "movie_name DESC"),
                    ("year_desc", "release_year DESC"),
                    ("year_asc", "release_year ASC"),
                    ("length_asc", "length ASC"),
                    ("length_desc", "length DESC")]

    for option, sorter in sort_options:
        if sort == option:
            sql += " ORDER BY " + sorter

    if sort == "rating_desc" or sort == "rating_asc" or sort == "best_sellers":
        sql = """
            SELECT movies.movie_id, movies.movie_name,
                   movies.release_year, movies.length,
                   movies.age_rating, movies.cost
            FROM movies
            JOIN rating_reviewers ON movies.movie_id = rating_reviewers.movie_id
        """
        if search:
            sql += " WHERE movies.movie_name LIKE ?"
        sql += " GROUP BY movies.movie_id"
        if sort == "rating_desc":
            sql += " ORDER BY AVG(rating_reviewers.percentage_rating) DESC"
        elif sort == "rating_asc":
            sql += " ORDER BY AVG(rating_reviewers.percentage_rating) ASC"
        else:
            sql += " ORDER BY movies.bestseller DESC, AVG(rating_reviewers.percentage_rating) DESC"
    
    cursor.execute(sql, filters)
    movies = cursor.fetchall()
    db.close()
    return render_template("movies.html", movies=movies)

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