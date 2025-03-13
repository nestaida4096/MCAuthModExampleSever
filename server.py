from flask import Flask, request, jsonify
import json
import os
from cryptography.fernet import Fernet

app = Flask(__name__)

# 暗号化キーを保存するファイル
KEY_FILE = "secret.key"
# 認証済みプレイヤーリストを保存するファイル
DATA_FILE = "authenticated_players.json.enc"

# 暗号化キーを読み込む or 生成する


def load_or_generate_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


# 暗号化・復号用のオブジェクト作成
KEY = load_or_generate_key()
CIPHER = Fernet(KEY)

# 認証済みプレイヤーリストの読み込み


def load_authenticated_players():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "rb") as f:
        encrypted_data = f.read()
    decrypted_data = CIPHER.decrypt(encrypted_data).decode()
    return json.loads(decrypted_data)

# 認証済みプレイヤーリストの保存


def save_authenticated_players(players):
    encrypted_data = CIPHER.encrypt(json.dumps(players).encode())
    with open(DATA_FILE, "wb") as f:
        f.write(encrypted_data)


# 初期化（データがない場合に空のリストを作成）
if not os.path.exists(DATA_FILE):
    save_authenticated_players([])


@app.route("/authenticatedPlayers", methods=["GET"])
def get_authenticated_players():
    return jsonify(load_authenticated_players())


@app.route("/auth", methods=["POST"])
def authenticate_player():
    data = request.get_json()
    if not data or "username" not in data:
        return jsonify({"error": "Invalid request"}), 400

    username = data["username"].strip()
    players = load_authenticated_players()
    if username not in players:
        players.append(username)
        save_authenticated_players(players)

    return jsonify({"message": f"{username} authenticated successfully"})


@app.route("/removeAuth", methods=["POST"])
def removeAuth():
    data = request.get_json()
    if not data or "username" not in data:
        return jsonify({"error": "Invalid request"}), 400

    username = data["username"].strip()
    players = load_authenticated_players()
    if username in players:
        players.remove(username)
        save_authenticated_players(players)

    return jsonify({"message": f"{username} removed successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
