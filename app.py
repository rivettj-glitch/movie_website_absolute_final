from flask import Flask, render_template, Response, request, redirect, url_for
import sqlite3

app = Flask(__name__)

favourites = []

db = sqlite3.connect("movie_website.db")
cursor = db.cursor()
cursor.execute("DELETE FROM comments WHERE comment_id > 90")
db.commit()
db.close()

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
    return render_template("index.html", best_sellers=best_sellers, favourites=favourites)

@app.route("/movies")
def movies():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()

    search = request.args.get("search", "")
    sort = request.args.get("sort")
    
    age_ratings = []
    sql = """
        SELECT DISTINCT age_rating 
        FROM movies
        ORDER BY age_rating ASC;"""
    cursor.execute(sql)
    results = cursor.fetchall()
    for rating in results:
        age_ratings.append(rating[0])

    genres = []
    sql = """
        SELECT genre_name
        FROM genres
        ORDER BY genre_name ASC;"""
    cursor.execute(sql)
    results = cursor.fetchall()
    for genre in results:
        genres.append(genre[0])

    selected_age_ratings = request.args.getlist("age_rating")
    selected_genres = request.args.getlist("genre")

    sql = """
        SELECT movie_id, movie_name, release_year, length, age_rating, cost
        FROM movies"""
    filters= ()
    if search:
        sql += " WHERE movie_name LIKE ?"
        filters = ("%" + search + "%",)

    if selected_age_ratings:
        if search:
            sql += " AND movies.age_rating IN ("
        else:
            sql += " WHERE movies.age_rating IN ("
        for rating in selected_age_ratings:
            sql += "?,"

        sql = sql[:-1]
        sql += ")"
        filters = filters + tuple(selected_age_ratings)

    if selected_genres:
        if search or selected_age_ratings:
            sql += " AND movies.movie_id IN ("
        else:
            sql += " WHERE movies.movie_id IN ("

        sql += """
            SELECT movie_id
            FROM movie_genres
            JOIN genres ON movie_genres.genre_id=genres.genre_id
            WHERE genre_name IN (
            """
        for genre in selected_genres:
            sql += "?,"
        sql = sql[:-1]
        sql += "))"
        filters = filters + tuple(selected_genres)

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
        filters =()

        if search:
            sql += " WHERE movies.movie_name LIKE ?"
            filters = filters + ("%" + search + "%",)
        if selected_age_ratings:
            if search:
                sql += " AND age_rating IN ("
            else:
                sql += " WHERE age_rating IN ("
            for rating in selected_age_ratings:
                sql += "?,"
            
            sql = sql[:-1]
            sql += ")"
            filters = filters + tuple(selected_age_ratings)

        if selected_genres:
                if search or selected_age_ratings:
                    sql += " AND movies.movie_id IN ("
                else:
                    sql += " WHERE movies.movie_id IN ("
        
                sql += """
                    SELECT movie_id
                    FROM movie_genres
                    JOIN genres ON movie_genres.genre_id=genres.genre_id
                    WHERE genre_name IN (
                    """
                for genre in selected_genres:
                    sql += "?,"
                sql = sql[:-1]
                sql += "))"
                filters = filters + tuple(selected_genres)

            
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
    return render_template("movies.html", movies=movies, age_ratings=age_ratings, genres=genres, favourites=favourites)

@app.route("/movie/<int:movie_id>", methods=["GET", "POST"])
def movie_details(movie_id):
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()

    if request.method == "POST":
        if "favourite" in request.form:
            if movie_id in favourites:
                favourites.remove(movie_id)
            else:
                favourites.append(movie_id)
        else:
            comment = request.form.get("comment")
            if comment:
                sql = """
                    INSERT INTO comments (comment, movie_id)
                    VALUES (?, ?)"""
                cursor.execute(sql, (comment, movie_id))
                db.commit()
        db.close()
        return redirect(url_for("movie_details", movie_id=movie_id))

    sql = """
        SELECT movie_id, movie_name, release_year, length, age_rating, cost
        FROM movies
        WHERE movie_id = ?"""
    cursor.execute(sql, (movie_id,))
    movie = cursor.fetchone()

    sql = """
        SELECT comment
        FROM comments
        WHERE movie_id = ?"""
    cursor.execute(sql, (movie_id,))
    comments = cursor.fetchall()

    sql = """
        SELECT reviewers.reviewer_name, rating_reviewers.percentage_rating
        FROM rating_reviewers
        JOIN reviewers ON rating_reviewers.reviewer_id=reviewers.reviewer_id
        WHERE rating_reviewers.movie_id = ?"""
    cursor.execute(sql, (movie_id,))
    reviews = cursor.fetchall()
    db.close()
    return render_template("movie_details.html", movie=movie, comments=comments, reviews=reviews, favourites=favourites)


@app.route("/favourite_movies")
def favourite_movies():
    db = sqlite3.connect("movie_website.db")
    cursor = db.cursor()
    favourites_movie_list = []
    for movie_id in favourites:
        sql = """
            SELECT movie_id, movie_name, release_year, length, age_rating, cost
            FROM movies
            WHERE movie_id = ?"""
        cursor.execute(sql, (movie_id,))
        movie = cursor.fetchone()
        if movie:
            favourites_movie_list.append(movie)
    db.close()
    return render_template("favourites.html", movies=favourites_movie_list)


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