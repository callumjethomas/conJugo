from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_session import Session
from mlconjug3 import Conjugator
from helpers import login_required, validate, generate_result
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import random

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///site.db")

# Initialize the conjugator
conjugator = Conjugator()

if __name__ == '__main__':
    app.run()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Basic infrastructure and account management


@app.route("/")
@login_required
def index():
    """Main page."""
    return render_template(
        "index.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error_message = "Must provide a username."
            return render_template(
                "login.html", error_message=error_message
            )

        # Ensure password was submitted
        elif not request.form.get("password"):
            error_message = "Must provide a password."
            return render_template(
                "login.html", error_message=error_message
            )

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            error_message = "Invalid username and/or password."
            return render_template(
                "login.html", error_message=error_message
            )

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template(
            "login.html"
        )


@app.route("/logout")
def logout():
    """Log current user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error_message = "Must provide a username."
            return render_template(
                "register.html", error_message=error_message
            )

        # Ensure username does not already exist
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if rows:
            error_message = "Username already exists. Please choose a different username."
            return render_template(
                "register.html", error_message=error_message
            )

        # Ensure password was submitted
        elif not request.form.get("password"):
            error_message = "Must provide a password."
            return render_template(
                "register.html", error_message=error_message
            )

        # Validate password
        if validate(request.form.get("password")) is False:
            error_message = "Password must be at least 8 characters long and contain at least 1 lowercase letter, 1 uppercase letter and 1 number."
            return render_template(
                "register.html", error_message=error_message
            )

        # Ensure password confirmation was confirmed
        elif not request.form.get("confirmation"):
            error_message = "Must confirm password."
            return render_template(
                "register.html", error_message=error_message
            )

        # Ensure confirmation matches password
        elif request.form.get("confirmation") != request.form.get("password"):
            error_message = "Password confirmation does not match."
            return render_template(
                "register.html", error_message=error_message
            )

        # Hash password
        hash = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")

        # Insert username and hash into users database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def change_pwd():
    """Change current password."""
    if request.method == "POST":
        # Ensure old password was submitted
        if not request.form.get("old-password"):
            error_message = "Must provide current password."
            return render_template(
                "account.html", error_message=error_message
            )

        # Check old password is correct
        # Query database for password hash
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", session.get("user_id"))

        # Ensure password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("old-password")):
            error_message = "Incorrect current password."
            return render_template(
                "account.html", error_message=error_message
            )

        # Ensure new password was submitted
        elif not request.form.get("new-password"):
            error_message = "Must provide new password."
            return render_template(
                "account.html", error_message=error_message
            )

        # Ensure password confirmation was confirmed
        elif not request.form.get("confirmation"):
            error_message = "Please confirm new password."
            return render_template(
                "account.html", error_message=error_message
            )

        # Ensure confirmation matches password
        elif request.form.get("confirmation") != request.form.get("new-password"):
            error_message = "Confirmation does not match new password."
            return render_template(
                "account.html", error_message=error_message
            )

        # Validate new password
        elif validate(request.form.get("new-password")) is False:
            error_message = "Password must be at least 8 characters long and contain at least 1 lowercase letter, 1 uppercase letter and 1 number."
            return render_template(
                "account.html", error_message=error_message
            )

        # Hash new password
        hash = generate_password_hash(request.form.get("new-password"))

        # Insert username and hash into users database
        db.execute(
            "UPDATE users SET hash = ? WHERE user_id = ?", hash, session.get("user_id")
        )

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("account.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete current user account."""
    if request.method == "POST":
        # Check password entered
        if not request.form.get("password"):
            error_message = "Must provide current password."
            return render_template(
                "delete.html", error_message=error_message
            )

        # Check password is correct
        # Query database for password hash
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", session.get("user_id"))

        # Ensure password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error_message = "Incorrect current password."
            return render_template(
                "delete.html", error_message=error_message
            )

        # Delete username and hash from users database and deletes user_id entries from scorecard and verbs tables
        db.execute("DELETE FROM scorecard WHERE user_id = ?", session.get("user_id"))
        db.execute("DELETE FROM verbs WHERE user_id = ?", session.get("user_id"))
        db.execute("DELETE FROM users WHERE user_id = ?", session.get("user_id"))

        # Log user out
        session.clear()

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("delete.html")


@app.route("/credits", methods=["GET"])
def credits():
    return render_template(
        "credits.html"
    )

# Main app functions

# Customising verb list


@app.route("/verb_list", methods=["GET"])
@login_required
def verb_list():
    """List verbs currently in the database."""
    verb_list = db.execute("SELECT name, type FROM verbs WHERE user_id = ? OR user_id IS NULL", session.get("user_id"))
    if any(verb['type'] == 'custom' for verb in verb_list):
        delete_all = True
    else:
        delete_all = False
    return render_template(
        "verb_list.html", verb_list=verb_list, delete_all=delete_all
    )


@app.route("/add_verb", methods=["POST"])
@login_required
def add_verb():
    """Add a custom verb to the database for current user. Maximum of 20 per user."""
    verb = request.form.get("verb")
    verb_list = db.execute("SELECT name, type FROM verbs WHERE user_id = ? OR user_id IS NULL", session.get("user_id"))
    custom_list = db.execute("SELECT name, type FROM verbs WHERE type = ? AND user_id = ?", 'custom', session.get("user_id"))
    if len(custom_list) >= 20:
        error_message = "Maximum number of custom verbs reached."
        return render_template(
            "verb_list.html", error_message=error_message, verb_list=verb_list, delete_all=True
        )
    for entry in custom_list:
        if entry['name'] == verb:
            error_message = "Verb already in list."
            return render_template(
                "verb_list.html", error_message=error_message, verb_list=verb_list
            )
    else:
        conj_verb = conjugator.conjugate(verb)
        if conj_verb:
            db.execute("""INSERT INTO verbs (name, type, user_id) VALUES (?, ?, ?)""", verb, 'custom', session.get("user_id"))
        else:
            error_message = "Not a valid verb."
            return render_template(
                "verb_list.html", error_message=error_message, verb_list=verb_list
            )
        return redirect(
            "verb_list"
        )


@app.route("/delete_verb", methods=["POST"])
@login_required
def delete_verb():
    """Delete a custom verb from the database for current user."""
    verb = request.form.get("verb")
    if request.form.get("delete_all") == "delete_all":
        db.execute("DELETE FROM verbs WHERE type = ? and user_id = ?", 'custom', session.get("user_id"))
        return redirect(
            "verb_list"
        )
    else:
        db.execute("DELETE FROM verbs WHERE name = ? AND user_id = ?", verb, session.get("user_id"))
        return redirect(
            "verb_list"
        )

# Conjugate function


@app.route("/conjugate", methods=["GET", "POST"])
@login_required
def conjugate():
    """Generate a conjugation table for a verb."""
    if request.method == "POST":
        verb = request.form.get("verb")
        # FALLOIR FIX
        if verb == 'falloir':
            return render_template(
                "falloir.html"
            )
        else:
            result = conjugator.conjugate(verb)
        if not result:
            error_message = "Not a valid verb."
            return render_template(
                "conjugate.html", error_message=error_message,
            )

        return render_template(
            "conjugate.html", result=result,
        )

    else:
        return render_template(
            "conjugate.html"
        )

# Practice function implementation


@app.route("/start", methods=["GET", "POST"])
@login_required
def start():
    """Setup verbs to use for practice."""
    user_id = session.get("user_id")
    # Set verbs to include (irregular, regular)

    if request.method == "POST":
        verb_types = request.form.getlist("verb_types")
        if not verb_types:
            error_message = "Must include at least one verb type."
            return render_template(
                "start.html", error_message=error_message
            )
        else:
            session['verb_types'] = verb_types

        # If custom is selected but there are no custom verbs, redirect to verb list
        if verb_types == ['custom']:
            custom_verbs = db.execute("SELECT name FROM verbs WHERE user_id = ?", session.get("user_id"))
            if not custom_verbs:
                error_message = "custom"
                return render_template(
                    "start.html", error_message=error_message
                )

        # Set moods to include
        verb_tenses = request.form.getlist("verb_tenses")
        if not verb_tenses:
            error_message = "Must choose at least one tense!"
            return render_template(
                "start.html", error_message=error_message
            )
        else:
            mood_list = []
            for entry in verb_tenses:
                if entry in ['Présent', 'Imparfait', 'Futur', 'Passé Simple']:
                    if 'Indicatif' in mood_list:
                        pass
                    else:
                        mood_list.append('Indicatif')
                else:
                    mood_list.append(entry)
            session["mood_list"] = mood_list

            # Set tenses to include
            tense_list = []
            for entry in verb_tenses:
                if entry in ['Présent', 'Imparfait', 'Futur', 'Passé Simple']:
                    if entry not in tense_list:
                        tense_list.append(entry)

            session["tense_list"] = tense_list

        # Get total possible permutations
        permutations = 0
        for verb in db.execute("SELECT name FROM verbs WHERE type IN (?) AND (user_id = ? OR user_id IS NULL)", verb_types, session.get("user_id")):
            if verb == "falloir":
                permutations += 8
            else:
                for entry in tense_list:
                    if entry in ['Présent', 'Imparfait', 'Futur', 'Passé Simple']:
                        permutations += 9
                for entry in mood_list:
                    if entry == "Conditionnel":
                        permutations += 9
                    if entry == "Subjonctif":
                        permutations += 18
                    if entry == "Imperatif":
                        permutations += 1
                    if entry == "Participe":
                        permutations += 5

        session["permutations"] = permutations
        # print("**** SESSION ****")
        # print(session)
        return redirect("practice")

    else:
        db.execute("DELETE FROM scorecard WHERE user_id = ?", user_id)
        # reset included verbs, moods and tenses
        session.pop("verb_types", None)
        session.pop("mood_list", None)
        session.pop("tense_list", None)
        session.pop("permutations", None)

        return render_template(
            "start.html",
        )


@app.route("/practice", methods=["GET", "POST"])
@login_required
def practice():
    """Practice conjugation of verbs."""
    user_id = session.get("user_id")
    permutations = session.get("permutations")

    # Get current score and total
    score = db.execute("SELECT SUM(points) FROM scorecard WHERE user_id = ?", user_id)[0]['SUM(points)']
    if score == None:
        score = 0
    total = db.execute("SELECT COUNT(*) FROM scorecard WHERE user_id = ?", user_id)[0]['COUNT(*)']
    if total == permutations:
        return redirect(
            "end"
        )

    result = generate_result()
    while db.execute("SELECT correct_answer FROM scorecard WHERE correct_answer = ? and user_id = ?", result[4], user_id):
        result = generate_result()

    db.execute("INSERT INTO scorecard (correct_answer, user_id) VALUES (?, ?)", result[4], user_id)

    return render_template(
        "practice.html", verb=result[0], pronoun=result[1], mood=result[2], tense=result[3], score=score, total=total
    )


@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    user_id = session.get("user_id")
    if request.method == "POST":
        total = db.execute("SELECT COUNT(*) FROM scorecard WHERE user_id = ?", user_id)[0]['COUNT(*)']
        scorecard_id = db.execute("SELECT MAX(scorecard_id) FROM scorecard WHERE user_id = ?", user_id)[0]['MAX(scorecard_id)']
        correct_answer = db.execute("SELECT correct_answer FROM scorecard WHERE scorecard_id = ?",
                                    scorecard_id)[0]['correct_answer']
        user_answer = request.form.get("user_answer")
        if user_answer == correct_answer:
            db.execute("UPDATE scorecard SET user_answer = ?, points = ? WHERE scorecard_id = ? AND user_id = ?",
                       user_answer, 1, scorecard_id, user_id)
            score = db.execute("SELECT SUM(points) FROM scorecard WHERE user_id = ?", user_id)[0]['SUM(points)']
            if score == None:
                score = 0
            return render_template(
                "correct.html", correct_answer=correct_answer, score=score, total=total
            )
        else:
            db.execute("UPDATE scorecard SET user_answer = ?, points = ? WHERE scorecard_id = ? AND user_id = ?",
                       user_answer, 0, scorecard_id, user_id)
            score = db.execute("SELECT SUM(points) FROM scorecard WHERE user_id = ?", user_id)[0]['SUM(points)']
            if score == None:
                score = 0
            return render_template(
                "incorrect.html", correct_answer=correct_answer, score=score, total=total
            )
    else:
        return redirect(
            "practice"
        )


@app.route("/scorecard", methods=["GET"])
@login_required
def scorecard():
    scorecard = db.execute("SELECT * FROM scorecard WHERE user_id = ?", session.get("user_id"))
    score = db.execute("SELECT SUM(points) FROM scorecard WHERE user_id = ?", session.get("user_id"))[0]['SUM(points)']
    total = db.execute("SELECT COUNT(points) FROM scorecard WHERE user_id = ?", session.get("user_id"))[0]['COUNT(points)']
    return render_template(
        "scorecard.html", scorecard=scorecard, score=score, total=total
    )


@app.route("/end", methods=["GET"])
@login_required
def end():
    score = db.execute("SELECT SUM(points) FROM scorecard WHERE user_id = ?", session.get("user_id"))[0]['SUM(points)']
    total = db.execute("SELECT COUNT(points) FROM scorecard WHERE user_id = ?", session.get("user_id"))[0]['COUNT(points)']
    return render_template("end.html", score=score, total=total)

# Error handling


@app.errorhandler(400)
def page_not_found(error):
    return render_template('error.html', code=405, message="We didn't understand that request.")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', code=404, message="That page could not be found.")


@app.errorhandler(405)
def page_not_found(error):
    return render_template('error.html', code=405, message="That method is not allowed.")


@app.errorhandler(500)
def page_not_found(error):
    return render_template('error.html', code=500, message="We don't know how to handle this request.")
