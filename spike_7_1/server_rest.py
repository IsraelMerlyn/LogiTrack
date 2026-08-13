import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_user_from_db(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, ultimo_login FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1], "email": row[2], "ultimo_login": row[3]}
    return None

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = get_user_from_db(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Usuario no encontrado"}), 404

if __name__ == "__main__":
    app.run(port=5000, debug=False)
