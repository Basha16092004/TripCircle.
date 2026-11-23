from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
CORS(app)


# ==========================================
# MYSQL CONNECTION
# ==========================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="basha012006@",
        database="tripcircle"
    )


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "message": "Backend is Running!",
        "project": "TripCircle",
        "status": "success"
    })


# ==========================================
# REGISTER
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No JSON data received"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "message": "Name, email and password are required"
        }), 400

    hashed_password = generate_password_hash(password)

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, hashed_password)
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({
            "message": "Registration successful!"
        }), 201

    except mysql.connector.IntegrityError:
        return jsonify({
            "message": "Email already registered"
        }), 409

    except Exception as e:
        return jsonify({
            "message": "Database error",
            "error": str(e)
        }), 500


# ==========================================
# LOGIN
# ==========================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No JSON data received"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if not user:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        if not check_password_hash(user["password"], password):
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Database error",
            "error": str(e)
        }), 500


# ==========================================
# CREATE TRIP
# ==========================================

@app.route("/api/trips", methods=["POST"])
def create_trip():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No JSON data received"
        }), 400

    user_id = data.get("user_id")
    name = data.get("name")
    start_location = data.get("start_location")
    destination = data.get("destination")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    members = data.get("members")
    progress = data.get("progress", 10)
    itinerary = data.get("itinerary", [])
    checks = data.get("checks", {})

    if not all([
        user_id,
        name,
        start_location,
        destination,
        start_date,
        end_date,
        members
    ]):
        return jsonify({
            "message": "Required trip details are missing"
        }), 400

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO trips (
                user_id,
                name,
                start_location,
                destination,
                start_date,
                end_date,
                members,
                progress,
                itinerary,
                checks
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                name,
                start_location,
                destination,
                start_date,
                end_date,
                members,
                progress,
                json.dumps(itinerary),
                json.dumps(checks)
            )
        )

        db.commit()

        trip_id = cursor.lastrowid

        cursor.close()
        db.close()

        return jsonify({
            "message": "Trip created successfully!",
            "trip_id": trip_id
        }), 201

    except Exception as e:
        return jsonify({
            "message": "Database error",
            "error": str(e)
        }), 500


# ==========================================
# GET USER TRIPS
# ==========================================

@app.route("/api/trips/<int:user_id>", methods=["GET"])
def get_user_trips(user_id):

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                name,
                start_location,
                destination,
                start_date,
                end_date,
                members,
                progress,
                itinerary,
                checks,
                created_at
            FROM trips
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,)
        )

        trips = cursor.fetchall()

        cursor.close()
        db.close()

        for trip in trips:

            if isinstance(trip["itinerary"], str):
                trip["itinerary"] = json.loads(trip["itinerary"])

            if isinstance(trip["checks"], str):
                trip["checks"] = json.loads(trip["checks"])

            if trip["start_date"]:
                trip["start_date"] = str(trip["start_date"])

            if trip["end_date"]:
                trip["end_date"] = str(trip["end_date"])

            if trip["created_at"]:
                trip["created_at"] = str(trip["created_at"])

        return jsonify({
            "message": "Trips fetched successfully!",
            "trips": trips
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Database error",
            "error": str(e)
        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)