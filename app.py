from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "project": "TripCircle",
        "message": "TripCircle Backend is Running!",
        "status": "success"
    })


@app.route("/api/test")
def test():
    return jsonify({
        "backend": "Python Flask",
        "message": "API is working successfully!"
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )