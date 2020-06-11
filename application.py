import os
import datetime
import pytz
import smtplib
import uuid


from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from helpers import apology, login_required, checkdate, change_day

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["checkdate"] = checkdate
app.jinja_env.filters["change_day"] = change_day

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


@app.route("/")
@login_required
def index():
    """Show user homepage"""

    # Obtain classes user is taking and store in my_classes (returns a list of dicts; each dict represents one class)
    # (If user is newly-registered and has no class in table "classes", db.execute returns None)
    my_classes = db.execute("SELECT classname FROM classes WHERE user_id = :user_id", user_id=session["user_id"])

    return render_template("index.html", classes=my_classes, username=db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]["username"], email=db.execute("SELECT email FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]["email"], hp=db.execute("SELECT hp FROM users WHERE user_id = :user_id", user_id=session["user_id"])[0]["hp"])


@app.route("/classcalendar/<string:classname>", methods=["GET", "POST"])
@login_required
def classcalendar(classname):
    """Show class calendar displaying pset availability of all classmates"""

    # Obtain current date, adjust for timezone, retrieve date only, change date format to yyyy-mm-dd
    date = datetime.datetime.now().astimezone(pytz.timezone("America/New_York")).date().strftime("%Y-%m-%d")

    # If user has not added class, prevent "Update Availability" from appearing in navbar. If user has added classes, remove "Add Class" button.
    if not db.execute("SELECT * FROM classes WHERE user_id = :user AND classname = :classname", user=session["user_id"], classname=classname):
        check = 0
    else:
        check = 1

    # Attempts to render template with elements from database, but if database is empty, renders without data
    try:
        # Obtain list of pset times and locations for a class (via joining updates and users tables)
        students = db.execute("SELECT * FROM updates INNER JOIN users ON updates.user_id = users.user_id WHERE classname=:classname AND date >= :date ORDER BY date ASC",
                              classname=classname, date=date)

        return render_template("classcalendar.html", students=students, classname=classname, user_id=session["user_id"], date=date, check=check)

    except:
        return render_template("classcalendar.html", classname=classname, check=check)


@app.route("/classhomepage/<string:classname>", methods=["GET", "POST"])
@login_required
def classhomepage(classname):
    """Show class homepage"""

    # Obtain list of ids of all students enrolled in a class
    rows = db.execute("SELECT * FROM classes WHERE classname=:classname", classname=classname)

    # If user has not added class, prevent "Update Availability" from appearing in navbar. If user has added classes, remove "Add Class" button.
    if not db.execute("SELECT * FROM classes WHERE user_id = :user AND classname = :classname", user=session["user_id"], classname=classname):
        check = 0
    else:
        check = 1

    # Create array of student information
    students = []

    for row in rows:
        students.append(db.execute("SELECT * FROM users WHERE user_id= :user_id", user_id=row["user_id"])[0])

    return render_template("classhomepage.html", students=students, classname=classname, check=check)

@app.route("/classupdate/<string:classname>", methods=["GET", "POST"])
@login_required
def classupdate(classname):
    """Allow student to update availability to meet to pset"""

    # User reached route via POST (via submitting update form)
    if request.method == "POST":

        # Server-side validation (ensure date, time, location fields are not empty)
        if not request.form.get("date"):
            return apology("Please fill in a date.")
        if not request.form.get("time"):
            return apology("Please fill in a time.")
        if not request.form.get("location"):
            return apology("Please fill in a location.")

        # If the user hasn't added the class yet (db.execute returns None), prevent user from updating availability
        rows = db.execute("SELECT * FROM classes WHERE user_id = :user_id AND classname = :classname", user_id = session["user_id"], classname=classname)
        if not rows:
            return apology("Please add the class before you update your availability.")

        # Insert the availability update into updates table
        db.execute("INSERT INTO updates (user_id, classname, date, time, location, notes) VALUES(:user_id, :classname, :date, :time, :location, :notes)",
                   user_id=session["user_id"], classname=classname, date=request.form.get("date"),
                   time=request.form.get("time"), location=request.form.get("location"), notes=request.form.get("notes"))

        # Display class calendar
        return classcalendar(classname)

    # User reached route via GET: display update form
    else:

        # If user has not added class, prevent "Update Availability" from appearing in navbar. If user has added classes, remove "Add Class" button.
        if not db.execute("SELECT * FROM classes WHERE user_id = :user AND classname = :classname", user=session["user_id"], classname=classname):
            check = 0
        else:
            check = 1

        return render_template("classupdate.html", classname=classname, check=check)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    # Validate that username is of length at least 1
    if len(request.args.get("username")) < 1:
        return jsonify(False)

    # Obtain all the usernames from table "users" which have already been taken
    existing_usernames = db.execute("SELECT username FROM users")

    # Validate that username does not already belong to a user in the database
    for existing_username in existing_usernames:
        if existing_username["username"] == request.args.get("username"):
            return jsonify(False)

    # Return true if username is of length at least 1 and is still available
    return jsonify(True)


@app.route("/deleteupdate/<string:classname>/<string:id>", methods=["POST"])
@login_required
def deleteupdate(classname, id):
    """Delete a particular entry in class calendar"""

    db.execute("DELETE FROM updates WHERE id=:id", id=id)

    return redirect("/classcalendar/" + classname)

@app.route("/deleteclass/<string:classname>", methods=["POST"])
@login_required
def deleteclass(classname):
    """Delete a class from user's homepage"""

    # Delete the class from the user in classes table
    db.execute("DELETE FROM classes WHERE classname=:classname AND user_id=:user_id", classname=classname, user_id=session["user_id"])

    # Delete all relevant availabilities linked to the class and the user in updates table
    db.execute("DELETE FROM updates WHERE classname=:classname AND user_id=:user_id", classname=classname, user_id=session["user_id"])

    return redirect("/")


@app.route("/friend/<string:user_id>", methods=["GET"])
@login_required
def friend(user_id):
    """Access another user's homepage """

    # Store the details of the target user whose homepage you are trying to access
    target_user = db.execute("SELECT * FROM users WHERE user_id = :user_id", user_id=user_id)[0]

    # If target user's user_id equals to current user's user_id, redirect to user's own homepage
    if session["user_id"] == target_user["user_id"]:
        return redirect("/")

    # If user is trying access another user's homepage, display the target user's homepage
    else:
        classes = db.execute("SELECT classname FROM classes WHERE user_id = :user_id", user_id=user_id)

        return render_template("friend.html", classes=classes, username=target_user["username"], email=target_user["email"], hp=target_user["hp"], user_id=user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search for classes"""

    # User reached route via GET: display search page
    if request.method == "GET":
        return render_template("search.html")

    # User reached route via POST (as by submitting search form via POST)
    else:
        classes = db.execute("SELECT * FROM class_list WHERE classname LIKE :classname ORDER BY classname ASC", classname="%" + request.form.get("classname") + "%")

        # Validate that class exists
        if not classes:
            return apology("There are no classes that match your search request. Please try again.")

        # Display list of classes that matches query
        return render_template("searched.html", classes=classes)

    # Redirect user to login page or homepage in case code somehow reaches this point
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via GET: display registration page
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting registration form via POST)
    else:

        # Validate user's inputs server-side
        if not request.form.get("username"):
            return apology("Username missing.")
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Password missing.")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")
        if not request.form.get("email"):
            return apology("Email missing.")


        # Insert new user into table "users" (id will equal None if username already exists and new row cannot be inserted)
        id = db.execute("INSERT INTO users (user_id, username, hash, email, hp) VALUES(:user, :username, :hash, :email, :hp)",
                        user=str(uuid.uuid4()), username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")), email=request.form.get("email"), hp=request.form.get("hp"))

        # Validate that username has not been taken
        if not id:
            return apology("Username already taken.")

    # Redirect user to login page
    return redirect("/")


@app.route("/changepw", methods=["GET", "POST"])
@login_required
def changepw():
    """Change password"""

    # User reached route via GET: display change password page
    if request.method == "GET":
        return render_template("changepw.html")

    # User reached route via POST (as by submitting change password form via POST)
    else:

        # Validate user's inputs
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Password missing.")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")

        # Update password of user in table users
        db.execute("UPDATE users SET hash = :hash WHERE user_id = :user_id",
                   user_id=session["user_id"], hash=generate_password_hash(request.form.get("password")))

        return redirect("/")

@app.route("/pset_on/<string:classname>", methods=["POST"])
@login_required
def pset_on(classname):
    """Show green button when user clicks Pset On button"""

    # Attempts to create dictionary list with table "updates", but if there are no rows that matches the WHERE conditions, escapes to except
    try:
        db.execute("UPDATE updates SET active = 1 WHERE user_id = :user AND id = :class_id AND classname = :classname AND date = :date",
                   user=session["user_id"], class_id=request.form.get("on_btn"), classname=classname, date=datetime.datetime.now().astimezone(pytz.timezone("America/New_York")).date().strftime("%Y-%m-%d"))

        return redirect("/classcalendar/" + classname)

    # Renders page indicating that no pset was scheduled at that time
    except:
        return apology("You have no pset scheduled for this time!")

@app.route("/pset_off/<string:classname>", methods=["POST"])
@login_required
def pset_off(classname):
    """Show red button when user clicks Pset Off button"""

    # Attempts to create dictionary list with table "updates", but if there are no rows that matches the WHERE conditions, escapes to except
    try:
        db.execute("UPDATE updates SET active = 0 WHERE user_id = :user AND id = :class_id AND classname = :classname AND date = :date",
                   user=session["user_id"], class_id=request.form.get("off_btn"), classname=classname, date=datetime.datetime.now().astimezone(pytz.timezone("America/New_York")).date().strftime("%Y-%m-%d"))

        return redirect("/classcalendar/" + classname)

    # Renders page indicating that no pset was scheduled at that time
    except:
        return apology("You have no pset scheduled for this time!")

@app.route("/email", methods=["GET", "POST"])
@login_required
def email():
    """Allows user to send an email to another user when at the other user's homepage"""

    # User reached route via "GET"
    if request.method == "GET":

        # Obtains user_id to use to render in email.html
        user_id = request.args.get("email_btn")

        return render_template("email.html", user_id=user_id)

    # User reached route via "POST"
    else:

        try:

            if not request.form.get("subject") or not request.form.get("message"):
                return apology("Please fill in subject and message fields!")

            # Obtains the user_id of intended recepient
            receiver_id = request.form.get("email_btn")

            # Obtains email of sender
            sender_email = db.execute("SELECT email FROM users WHERE user_id = :user", user=session["user_id"])

            # Obtains email of intended recepient
            receiver_email = (db.execute("SELECT email FROM users WHERE user_id = :user", user=receiver_id))

            # Create message object and attaches From, To, Subject, and Message elements
            msg = MIMEMultipart()
            msg['From'] = "yalepsetparty@gmail.com"
            msg['To'] = receiver_email[0]["email"]
            msg['Subject'] = request.form.get("subject")

            # Signs off every email with a line that shows sender_email so the recepient can reply
            message = request.form.get("message") + "\n\nContact me at " + sender_email[0]["email"]


            # Attaches message to msg
            msg.attach(MIMEText(message))

            # Initiates server
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.ehlo()

            # Logs into the psetparty official email
            server.login("yalepsetparty@gmail.com", "aldmirtat")

            # Sends email to receiver_email, then quits
            server.sendmail("yalepsetparty@gmail.com", receiver_email[0]["email"], msg.as_string())
            server.quit()

            return render_template("email_success.html")

        except:

            return apology("Email could not be sent.")


@app.route("/addclass/<string:classname>", methods=["GET"])
@login_required
def addclass(classname):
    """Allow user to add the class to his user homepage"""

    db.execute("INSERT INTO classes (user_id, classname) VALUES(:user_id, :classname)",
               user_id=session["user_id"], classname=classname)

    return redirect("/")
