"""
Number Guessing Game — Flask backend
-------------------------------------
Har naye game me:
  1. Ek random "max range" choose hota hai jo 10 se divisible hota hai
     (jaise 10, 20, 30, ... 100, ... 1000). Range hamesha 1 se start hota hai.
  2. Us range ke andar ek random "secret number" choose hota hai.
  3. User guess karta hai, hum bata dete hai "too high" / "too low" / "correct".

Game state session me store hota hai (per-browser), taaki alag alag
users ek dusre ka game na dekhein.
"""

from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
# Production me isse environment variable se lena, yaha demo ke liye direct.
app.secret_key = "change-this-secret-key-in-production"


def generate_range():
    """1 se lekar kisi bhi 10-se-divisible number tak ek random range banata hai."""
    possible_max_values = list(range(10, 1001, 10))  # 10, 20, 30 ... 1000
    return random.choice(possible_max_values)


def start_new_game():
    """Naya secret number + range set karke session me save karta hai."""
    max_range = generate_range()
    secret_number = random.randint(1, max_range)

    session["secret_number"] = secret_number
    session["max_range"] = max_range
    session["attempts"] = 0

    return max_range


@app.route("/")
def index():
    max_range = start_new_game()
    return render_template("index.html", max_range=max_range)


@app.route("/guess", methods=["POST"])
def guess():
    if "secret_number" not in session:
        return jsonify({"error": "Game session nahi mili, page refresh karo."}), 400

    data = request.get_json(silent=True) or {}
    raw_guess = data.get("guess")

    try:
        user_guess = int(raw_guess)
    except (TypeError, ValueError):
        return jsonify({"result": "invalid", "message": "Sirf number likho!"}), 400

    secret_number = session["secret_number"]
    max_range = session["max_range"]

    session["attempts"] += 1
    attempts = session["attempts"]

    if user_guess < 1 or user_guess > max_range:
        return jsonify({
            "result": "invalid",
            "message": f"Range ke andar guess karo: 1 se {max_range} tak!",
            "attempts": attempts,
        })

    if user_guess < secret_number:
        return jsonify({
            "result": "low",
            "message": "Thoda aur upar jao! 📈",
            "attempts": attempts,
        })

    if user_guess > secret_number:
        return jsonify({
            "result": "high",
            "message": "Thoda neeche aao! 📉",
            "attempts": attempts,
        })

    return jsonify({
        "result": "correct",
        "message": f"Sahi jawab! Number tha {secret_number} 🎉",
        "attempts": attempts,
    })


@app.route("/new-game", methods=["POST"])
def new_game():
    max_range = start_new_game()
    return jsonify({"max_range": max_range})


if __name__ == "__main__":
    app.run(debug=True)