from flask import Flask, render_template, request, redirect, url_for, session
import csv
import os
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noumanshariff7411@gmail.com'
app.config['MAIL_PASSWORD'] = 'qgob gpxj jgqy zhoq'  # App password
app.config['MAIL_DEFAULT_SENDER'] = 'noumanshariff7411@gmail.com'

mail = Mail(app)

@app.route("/")
def home():
    return render_template("index.html", current_page="home")

@app.route("/projects")
def projects():
    return render_template("projects.html", current_page="projects")

@app.route("/appointment", methods=["GET", "POST"])
def appointment():
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        contact = request.form["contact"]
        query = request.form["query"]

        file_path = "appointments.csv"
        next_id = 1

        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    try:
                        next_id = int(last_row[0]) + 1
                    except:
                        next_id = len(rows) + 1

        # Save to CSV
        with open(file_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([next_id, name, address, contact, query])

        # Send email
        try:
            msg = Message("New Appointment Booking",
                          recipients=['your_email@gmail.com'])  # Replace with your email
            msg.body = f"""
            New appointment booked:
            Name: {name}
            Address: {address}
            Contact: {contact}
            Query: {query}
            """
            mail.send(msg)
            print("✅ Email sent!")
        except Exception as e:
            print("❌ Email sending failed:", e)

        return redirect(url_for("thankyou"))

    return render_template("appointment.html", current_page="appointment")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "pass123":
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("login_failed.html")

    return render_template("login.html", current_page="login")

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    query = request.args.get("search", "").lower()
    appointments = []

    try:
        with open("appointments.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if not query or any(query in field.lower() for field in row):
                    appointments.append(row)
    except FileNotFoundError:
        pass

    return render_template("admin.html", appointments=appointments, search=query)


@app.route("/delete", methods=["POST"])
def delete_appointment():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    delete_id = request.form.get("id")

    appointments = []
    try:
        with open("appointments.csv", "r") as file:
            reader = csv.reader(file)
            appointments = [row for row in reader if row[0] != delete_id]
    except FileNotFoundError:
        pass

    with open("appointments.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(appointments)

    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
