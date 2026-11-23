from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)


# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="basha012006@",
        database="tripcircle"
    )


# Home
@app.route("/")
def home():
    return jsonify({
        "message": "Backend is Running!",
        "project": "TripCircle",
        "status": "success"
    })


# =========================
# REGISTER API
# =========================
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

        sql = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (name, email, hashed_password))
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


# =========================
# LOGIN API
# =========================
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

        sql = """
        SELECT id, name, email, password
        FROM users
        WHERE email = %s
        """

        cursor.execute(sql, (email,))
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


# Start server
if __name__ == "__main__":
    app.run(debug=True)