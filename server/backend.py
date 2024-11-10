from flask import Flask, render_template, request, jsonify, flash, redirect
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import cv2
import base64
import numpy as np
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotifylogic import SpotifyActions
import pyautogui 
import random

app = Flask(__name__)

# Connect Database
import mysql.connector

# Establish a connection
conn = mysql.connector.connect(
    host='localhost',
    user="root",
    password='madhacks2024',
    database='ListenTua',

)
db1 = conn.cursor()

CLIENT_ID = '2486129522ca4ed8bf027362ebfd60b1'
CLIENT_SECRET = '76bd17dcb73548d49f7a45c22ab03c96'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

app.secret_key = 'your_secret_key_here'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         redirect_uri=REDIRECT_URI,
                         scope="user-read-private user-library-read user-modify-playback-state user-read-playback-state user-read-email streaming")

spotifyObj = SpotifyActions()

@app.route("/register", methods=["POST"])
def register():
    body = request.get_json()
    if not body.get("username"):
        return jsonify({"message": "Username is required"}), 400
    elif not body.get("password"):
        return jsonify({"message": "Password is required"}), 400

    try:
        # Check if username exists
        db1.execute(f"SELECT * FROM users")
        rows = db1.fetchall()
        if any(row[0] == body.get("username") for row in rows):
            return jsonify({"message": "Username already exists"}), 409
        # Hash the password
        hashed_password = generate_password_hash(body.get("password"))

        print("Username:", body.get("username"))
        print("Hashed Password:", hashed_password)
        # Insert the new user
        db1.execute(f"INSERT INTO users values (%s,%s)", (body.get("password"), hashed_password))
        conn.commit()

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    return jsonify({"message": "Successfully registered"}), 200


@app.route("/login", methods=["POST"])
def login():

    # Ensure username was sumbitted
    if not request.form.get("username"):
        response = {
            "message": "Username is required"
        }
        return response, 400

    # Ensure password was submitted
    elif not request.form.get("password"):
        response = {
            "message": "password is required"
        }
        return response, 400

    # Query database for username
    db1.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
    # Ensure username exists and password is correct
    rows = db1.fetchall()
    for row in rows:
        if not row[0] or not check_password_hash(row[1], request.form.get("password")):
             response = {
                "message": "Invalid username or password"
            }
        return response, 403
    # Remember which user has logged in
    response ={
        "message" : "Successfully Logged In",
        "username" : request.form.get("username")
    }
    return response, 200


@app.route('/')
def index():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    spotifyObj.setToken(access_token)
    return access_token #need to return another redirect URL here maybe?

@app.route('/search', methods=["POST"])
def search():
    access_token = spotifyObj.access_token
    if not access_token:
        return jsonify({"error": "Access token missing or expired"}), 400
    body = request.get_json()
    query = body.get("query", "pop") #default to pop
    mode = body.get("mode", "")
    songs = spotifyObj.getSongs(query=query, mode=mode)
    return jsonify(songs)

@app.route('/screenshot', methods=["POST"])
def screenshot():
    screenshot = pyautogui.screenshot()
    randomInt = random.randint(1,10000)
    try:
        screenshot.save(f'screenshot{randomInt}.png')
        return {"status_code":200, "message":"Save image"}
    except:
        return {"status_code":500, "message":"Server error"}

@app.route("/screen", methods=["POST"])
def submitScreen():
    requestBody = request.json()
    print(requestBody)

@app.route("/playnext", methods = [""])
def playSong(sp):
    pass

if __name__ == "__main__":
    app.run(debug=True)
