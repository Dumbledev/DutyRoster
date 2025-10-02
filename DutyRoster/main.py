from flask import Flask, render_template, request, session, redirect, url_for
from kenobi import KenobiDB
import uuid
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
User = KenobiDB("user.db")
Roster = KenobiDB("roster.db")

bcrypt = Bcrypt(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/home')
def home():
    is_user()
    user_id = session["_id"]
    rosters = []
    all_rosters = Roster.all()
    for i in all_rosters:
        for j in i["staffs"]:            
            if user_id in j["_id"]:
                rosters.append(i)
            else:
                print("no user")
    user = User.search("_id", user_id)
    return render_template("home.html", user=user[0], rosters=rosters, all_rosters=all_rosters)

# admin
@app.route("/admin")
def admin():
    is_admin_user()
    admin = User.search("_id", session["_id"])
    users = User.all()
    rosters = Roster.all()
    staffs = User.find_all("role", ["user"])
    return render_template("admin/admin.html", 
                           users=users, rosters=rosters, 
                           admin=admin[0], staffs=staffs)

@app.route("/new_roster", methods=["GET", "POST"])
def new_roster():
    is_admin_user()
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        # department = request.form["department"]
        academic = request.form["academic"]

        Roster.insert({
            "_id":str(uuid.uuid4()),
            "title":title,
            "description":description,
            # "department":department,
            "academic":academic,
            "staffs":[{"_id":"None"}],
            "duties":{
                "Monday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}}, 
                "Tuesday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}}, 
                "Wednesday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}},
                "Thursday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}},
                "Friday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}}, 
                "Saturday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}},
                "Sunday":{"9:00":{}, "11:00":{}, "1:00":{}, "3:00":{}, "5:00":{}}
            },
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deleted_at":"",
            })
        return redirect("/rosters")
    else:
        return render_template("admin/new_roster.html")


@app.route("/rosters")
def rosters():
    rosters = Roster.all()
    return render_template("admin/rosters.html", rosters=rosters)

@app.route("/roster_admin/<id>")
def roster_admin(id):
    roster = Roster.search("_id", id)
    if len(roster) == 0:
        return render_template("400.html", "No Duty Roster Found")
    else:
        roster = roster[0]
        roster["staffs"].pop(0)
        return render_template("admin/roster_admin.html", roster=roster)


@app.route("/update_roster/<id>")
def update_roster(id):            
    roster = Roster.search("_id", id)
    if len(roster) == 0:
        return render_template("400.html", "No Duty Roster Found")          
    return render_template("admin/update_roster.html", roster=roster[0])

@app.route("/update_roster_handler", methods=["GET", "POST"])
def update_roster_handler():
    if request.method == "POST":
        id = request.form["id"]
        Roster.update("_id", id, {"title": request.form["title"]})
        Roster.update("_id", id, {"description": request.form["description"]})
        Roster.update("_id", id, {"academic": request.form["academic"]})
        # Roster.update("_id", id, {"department": request.form["department"]})
        Roster.update("_id", id, {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return redirect("/rosters")    

@app.route("/delete_roster/<id>")
def delete_roster(id):
    roster = Roster.search("_id", id)
    if len(roster) == 0:
        return render_template("400.html", "No Duty Roster Found")
    Roster.remove("_id", id)
    rosters = Roster.all()
    # msg = f"{roster["title"]} Deleted Sucessfully!!"
    return render_template("admin/rosters.html", rosters = rosters, msg = "msg")

@app.route("/roster_add_staff/<id>")
def roster_add_staff(id):
    roster = Roster.search("_id", id)    
    staffs = User.find_all("academic", [roster[0]['academic']])
    roster_staffs = roster[0]['staffs']
    matching_items = []
    
    target_ids = {d['_id'] for d in staffs}
    staffs_ids = {d['_id'] for d in roster_staffs}
    print(target_ids)
    print(staffs_ids)
    ids = target_ids - staffs_ids
    for i in ids:
        s = User.search("_id",i)
        matching_items.append(s[0])
    print(matching_items)

    # for i in roster_staffs:
    #     if i["_id"] not in target_ids:
    #         matching_items.append(i)
    return render_template("admin/roster_add_staff.html", staffs=matching_items, id=id)

@app.route("/add_staff_handler", methods=["POST"])
def add_staff_handler():
    if request.method == "POST":
        roster_id = request.form["id"]
        roster = Roster.search("_id", roster_id)
        roster_staffs =  roster[0]['staffs']  
        staff_ids = request.form.getlist("staffs")
        staffs_to_add = []
        print(staff_ids)
        for i in staff_ids:
            staff_to_add = User.search("_id", i)
            staffs_to_add.append(staff_to_add[0])                

        staffs = roster_staffs + staffs_to_add
        print(staffs)
        Roster.update("_id", roster_id, {"staffs":staffs})
        return redirect("/rosters")

@app.route("/remove_staff/<roster_id>/<staff_id>")
def remove_staff(roster_id, staff_id):
    roster = Roster.search("_id", id)
    staff = User.search("id", staff_id)
    if len(roster) == 0:
        return render_template("400.html", "No Duty Roster Found")   
    staffs = roster[0]["Staffs"]
    new_stafs = [s for s in staffs if s.get('_id') != staff["id"]]
    Roster.update("_id", id, {"Staffs":new_stafs}) 
    return redirect("/roster_admin/"+roster_id)


@app.route("/add_duty/<roster_id>/<day>/<time>", methods=["GET", "POST"])
def add_duty(day, roster_id, time):
    if request.method == "POST":
        name = request.form["name"]
        roster = Roster.search("_id", roster_id)
        if len(roster) == 0:
            return render_template("400.html", "No Duty Roster Found") 
        roster_duties = roster[0]["duties"]
        roster_duties[day][time] = name
        Roster.update("_id", roster_id, {"duties":roster_duties}) 
        return redirect("/roster_admin/"+roster_id)
    else:
        roster = Roster.search("_id", roster_id)
        return render_template("admin/add_duty.html", staffs = roster[0]['staffs'], roster_id=roster_id,day=day, time=time)

# end_admin


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        academic = request.form["academic"]

        users = User.search("email", email)
        if len(users) != 0:
            return render_template("register.html", err = "Credentials Already In Use, Please Choose a Different Email")

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        User.insert({
            "_id": str(uuid.uuid4()),
            "name":name,
            "email":email, 
            "password":hashed_pw,
            "doctype":"user",
            "role":role,
            "academic":academic,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deleted_at":"",           
            })
        return redirect("/login")
    else:
        return render_template('register.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        user = User.search("email", email)
        if len(user) == 0 or bcrypt.check_password_hash(user[0]["password"], password) == False:
            return render_template("login.html", err = "Invalid username/password combination")
        else:
            user = user[0]
            session["logged_in"] = True
            session["_id"] = user["_id"]
            session['role'] = user['role']
            if user["role"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/home")
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    # Remove all keys from the session dictionary
    session.clear()
    return redirect(url_for('login'))

   
def is_admin_user():
    if 'logged_in' not in session or session["role"] != 'admin':
        return redirect("/login") 

def is_user():
    if 'logged_in' not in session or session["role"] != 'admin':
        return redirect("/login") 

if __name__ == "__main__":
    app.run(debug=True)


# db.find_all('color', ['blue', 'red'])
# db.find_any('color', ['blue', 'red'])
# db.search('color', 'blue')

# db.all(limit=10, offset=0)  # With pagination
# db.all()  # No pagination

# db.purge()

# db.update('name', 'Ryan', {'color': 'dark'})
# db.remove('name', 'Oden')
# db.insert({'name': 'Oden', 'color': 'blue'})
# db.insert_many([
#     {'name': 'Ryan', 'color': 'red'},
#     {'name': 'Tom', 'color': 'green'}
# ])