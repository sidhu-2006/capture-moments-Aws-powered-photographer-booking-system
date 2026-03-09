from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import boto3
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "capturemomentssecret"

# -----------------------------
# Connect to DynamoDB Local
# -----------------------------
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8001",
    region_name="us-west-2",
    aws_access_key_id="dummy",
    aws_secret_access_key="dummy"
)

# -----------------------------
# Tables
# -----------------------------
bookings_table = dynamodb.Table("PhotographerBookings")
photographers_table = dynamodb.Table("Photographers")
users_table = dynamodb.Table("Users")


# -----------------------------
# LOGIN ROUTE
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:
            response = users_table.get_item(Key={"email": email})
            user = response.get("Item")

            if not user:
                return render_template("login.html", error="User not found")

            if check_password_hash(user["password"], password):
                session["user"] = user["username"]  # store username instead of email
                return redirect(url_for("photographers"))
            else:
                return render_template("login.html", error="Incorrect password")

        except Exception as e:
            print("Login error:", e)
            return render_template("login.html", error="Login failed")

    return render_template("login.html")


# -----------------------------
# REGISTER ROUTE
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            response = users_table.get_item(Key={"email": email})

            if "Item" in response:
                return render_template("register.html", error="User already exists")

            hashed_password = generate_password_hash(password)

            users_table.put_item(
                Item={
                    "email": email,
                    "username": username,
                    "password": hashed_password
                }
            )

            session["user"] = username  # store username instead of email
            return redirect("/photographers")

        except Exception as e:
            print("Register error:", e)
            return render_template("register.html", error="Registration failed")

    return render_template("register.html")


# -----------------------------
# LOGOUT ROUTE
# -----------------------------
@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect(url_for("login"))


# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/")
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    return redirect(url_for("photographers"))


# -----------------------------
# VIEW PHOTOGRAPHERS
# -----------------------------
@app.route("/photographers")
def photographers():

    if "user" not in session:
        return redirect(url_for("login"))

    try:
        response = photographers_table.scan()
        photographers = response.get("Items", [])
    except Exception as e:
        print("Fetch photographers error:", e)
        photographers = []

    return render_template("photographers.html", photographers=photographers)


# -----------------------------
# ADD PHOTOGRAPHER
# -----------------------------
@app.route("/add_photographer", methods=["GET", "POST"])
def add_photographer():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        photographer_id = str(uuid.uuid4())

        name = request.form["name"]
        specialization = request.form["specialization"]
        location = request.form["location"]
        price = request.form["price"]

        try:
            photographers_table.put_item(
                Item={
                    "id": photographer_id,
                    "name": name,
                    "specialization": specialization,
                    "location": location,
                    "price": price
                }
            )

            return redirect(url_for("photographers"))

        except Exception as e:
            print("Add photographer error:", e)

    return render_template("add_photographer.html")


# -----------------------------
# BOOK PHOTOGRAPHER PAGE
# -----------------------------
@app.route("/book_photographer")
def book_photographer():

    if "user" not in session:
        return redirect(url_for("login"))

    photographer_id = request.args.get("id")

    try:
        response = photographers_table.get_item(Key={"id": photographer_id})
        photographer = response.get("Item")
    except Exception as e:
        print("Fetch photographer error:", e)
        photographer = None

    return render_template("book.html", photographer=photographer)


# -----------------------------
# SAVE BOOKING
# -----------------------------
@app.route("/book", methods=["POST"])
def book():

    try:

        data = request.get_json()
        booking_id = str(uuid.uuid4())

        bookings_table.put_item(
            Item={
                "booking_id": booking_id,
                "photographer_id": str(data["photographer_id"]),
                "name": str(data["name"]),
                "email": str(data["email"]),
                "phone": str(data["phone"]),
                "location": str(data["location"])
            }
        )

        return jsonify({"message": "Booking Successful"})

    except Exception as e:
        print("Booking error:", e)
        return jsonify({"message": "Booking Failed"})


# -----------------------------
# VIEW BOOKINGS
# -----------------------------
@app.route("/bookings")
def view_bookings():

    if "user" not in session:
        return redirect(url_for("login"))

    try:

        response = bookings_table.scan()
        bookings = response.get("Items", [])

        for booking in bookings:

            photographer_id = booking.get("photographer_id")

            if photographer_id:

                photographer = photographers_table.get_item(
                    Key={"id": photographer_id}
                )

                photographer_data = photographer.get("Item")

                if photographer_data:
                    booking["photographer_name"] = photographer_data["name"]
                else:
                    booking["photographer_name"] = "Unknown"

            else:
                booking["photographer_name"] = "Not Selected"

    except Exception as e:
        print("Fetch bookings error:", e)
        bookings = []

    return render_template("bookings.html", bookings=bookings)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)