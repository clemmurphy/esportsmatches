import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import requests
import datetime
import operator
from helpers import login_required, apology
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

API_KEY = "BCApjQWYEFEwNjioGJHJKCCT0APkpimhsUcpvkrNrp_QsazFrCs"


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    
    if request.method == "GET":
        team_ids_dict = {"LoL": "394", "CSGO": "3217", "R6": "126928", "Dota": "1664", "Valorant": "128537"}
        team_ids_list = ["394", "3217", "126928", "1664", "128537"]
        matches = []
        mtmp = []

    # if logged in, use user settings
    if "user_id" in session:
        loginstatus = True
        # query database for user settings
        db = sqlite3.connect("esportstracker.db")
        db.row_factory = sqlite3.Row
        usersettings = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchall()
        db.close

        # populate temporary matches table from API based on settings
        index = 0
        for x in usersettings[0][3:]:
            if x == 1:
                mtmp.append(requests.get("https://api.pandascore.co/teams/" + team_ids_list[index] + "/matches?search[status]=not_started&token=" + API_KEY).json())
            index += 1

    #if not logged in, default to all matches
    else:
        loginstatus = False
        # populate matches table from API
        for x in team_ids_list:
            res = requests.get("https://api.pandascore.co/teams/" + x + "/matches?search[status]=not_started&token=" + API_KEY).json()
            if res:
                mtmp.append(res)

    # parse JSON data into matches data for table
    c = 0
    for title_matches in mtmp:
        for x in title_matches:
            matches.append({})
            matches[c]['league_image_url'] = x['league']['image_url']
            matches[c]['league_name'] = x['league']['name']
            matches[c]['league_url'] = x['league']['url']
            matches[c]['videogame'] = x['videogame']['name']
            matches[c]['number_of_games'] = x['number_of_games']
            matches[c]['en_stream_url'] = x['streams']['english']['raw_url']

            # convert start time and date to readable string
            t = datetime.datetime.strptime(x['begin_at'], "%Y-%m-%dT%H:%M:%S%z")
            matches[c]['dateobject'] = t
            matches[c]['starttime'] = t.strftime("%H:%M")
            matches[c]['startdate'] = t.strftime("%d-%m-%Y")

            # assign the opponent and image
            if "fnatic" or "Fnatic" in x['opponents'][0]['opponent']['name']:
                if len(x['opponents']) > 1:
                    if x['opponents'][1]['opponent']['name'] != None:
                        matches[c]['opponent_name'] = x['opponents'][1]['opponent']['name']

                        # if they have no image, set default image
                        if x['opponents'][1]['opponent']['image_url'] != None:
                            matches[c]['opponent_image_url'] = x['opponents'][1]['opponent']['image_url']
                        else:
                            matches[c]['opponent_image_url'] = "./static/img/default-logo.png"

                # if they have no name or TBD, set TBD and default image
                else:
                    matches[c]['opponent_name'] = 'TBD'
                    matches[c]['opponent_image_url'] = "./static/img/default-logo.png"

            else:
                matches[c]['opponent_name'] = x['league.opponents'][0]['opponent']['name']
                # if they have no image, set default image
                if x['opponents'][0]['opponent']['image_url'] != None:
                    matches[c]['opponent_image_url'] = x['opponents'][0]['opponent']['image_url']
                else:
                    matches[c]['opponent_image_url'] = "./static/img/default-logo.png"

            c += 1

        # sort match list by start date
        matches.sort(key=operator.itemgetter('dateobject'))

    # pass matches to index template
    return render_template("index.html", matches=matches, loginstatus=loginstatus,)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any logged in user
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # query database for username and password
        db = sqlite3.connect("esportstracker.db")
        db.row_factory = sqlite3.Row
        usercheck = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        db.close

        if len(usercheck) != 1:
            return apology("No user with that name found!", 400)
        
        if check_password_hash(usercheck[0]["hash"], request.form.get("password")):
            # Remember which user has registered
            session["user_id"] = usercheck[0]["id"]
            # Redirect user to home page
            return redirect("/")
        else:
            return apology("Password incorrect!", 400)

        # redirect to home page
        return redirect("/")

    else:   
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password is correctly confirmed
        elif request.form.get("password") != request.form.get("confirm_password"):
            return apology("passwords do not match", 400)

        # Ensure password is minimum length
        elif len(request.form.get("password")) < 4:
            return apology ("passwords must be four characters minimum", 403)

        # Query database for username
        db = sqlite3.connect("esportstracker.db")
        matches = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        # Ensure user does not already exist
        if len(matches.fetchall()) > 0:
            db.close
            return apology("user already exists, please log in", 400)
        db.close

        # Add new user into database using password hash
        pw_hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        db = sqlite3.connect("esportstracker.db")
        db.execute("INSERT INTO users (username, hash, lol, csgo, r6, dota, valorant) VALUES(?,?,?,?,?,?,?)", (request.form.get("username"), pw_hashed, request.form.get("lol"), request.form.get("csgo"), request.form.get("r6"), request.form.get("dota"), request.form.get("valorant")))
        db.commit()

        db.row_factory = sqlite3.Row
        newreg = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
        db.close

        # Remember which user has registered
        session["user_id"] = newreg[0]["id"]

        # Redirect user to home page
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect ("/")

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # default to not displaying message
    usermessage = False

    # If user has submitted a form
    if request.method == "POST":

        # check to see if user is updating password
        if request.form.get("change_password"):

            # Ensure password is correctly confirmed
            if request.form.get("change_password") != request.form.get("confirm_change_password"):
                return apology("passwords do not match", 400)

            # Ensure password is minimum length
            elif len(request.form.get("change_password")) < 4:
                return apology ("passwords must be four characters minimum", 403)

            # Hash password
            pw_hashed = generate_password_hash(request.form.get("change_password"), method='pbkdf2:sha256', salt_length=8)

            # update password in database
            db = sqlite3.connect("esportstracker.db")
            db.execute("UPDATE users SET hash=? WHERE id=?", (pw_hashed, session["user_id"]))
            db.commit()
            db.close
        
        # update game settings in database
        db = sqlite3.connect("esportstracker.db")
        db.execute("UPDATE users SET (lol, csgo, r6, dota, valorant)=(?,?,?,?,?) WHERE id=?", ( request.form.get("lol"), request.form.get("csgo"), request.form.get("r6"), request.form.get("dota"), request.form.get("valorant"), session["user_id"]))
        db.commit()
        db.close

        # Tell user their settings have been updated
        usermessage = True

    # query database for user settings to display
    db = sqlite3.connect("esportstracker.db")
    db.row_factory = sqlite3.Row
    usersettings = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    db.close

    return render_template("settings.html", usersettings=usersettings, usermessage=usermessage)