from flask import Flask, render_template, request, jsonify, redirect, url_for
import face_auth  # Ensure this module has the necessary functions for face recognition
import base64
import cv2
import numpy as np
import hashlib
import os

app = Flask(__name__)

# In-memory storage for demonstration purposes
# In a real application, use a database to store user details securely
users = {}

IMAGE_SAVE_DIR = 'captured_images'

if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

def save_image(username, img_data, img_type):
    """Saves the captured image to the specified directory."""
    img_path = os.path.join(IMAGE_SAVE_DIR, f"{username}_{img_type}.png")
    with open(img_path, "wb") as f:
        f.write(img_data)
    return img_path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        image_data = data.get('image')

        print(f"Received data - Username: {username}, Password: {password}, Email: {email}, Phone: {phone}")

        if username and password and email and phone and image_data:
            image_data = base64.b64decode(image_data.split(',')[1])
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Save the image to the directory
            save_image(username, image_data, 'registration')

            # Save the face encoding with the username
            success = face_auth.capture_face_from_image(img, username)
            if success:
                # Hash the password for security
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                users[username] = {"password": hashed_password, "email": email, "phone": phone}
                print(f"User registered - Username: {username}, Hashed Password: {hashed_password}")
                print(f"Users dict: {users}")
                return jsonify({"message": f"User {username} registered successfully!", "redirect": url_for('home')})
            else:
                return jsonify({"message": "Registration failed."}), 400
        return jsonify({"message": "All fields are required for registration."}), 400

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.json
    image_data = data.get('image')
    username = data.get('username')
    password = data.get('password')

    print(f"Login attempt - Username: {username}, Password: {password}")

    if image_data:
        image_data = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Save the image to the directory
        save_image("login_attempt", image_data, 'login')

        # Authenticate the user using the captured image
        authenticated_user = face_auth.authenticate_user_from_image(img)
        if authenticated_user:
            return jsonify({"message": f"Welcome, {authenticated_user}!", "redirect": url_for('home')})
        else:
            return jsonify({"message": "Authentication failed."}), 400

    if username and password:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        print(f"Hashed Password: {hashed_password}")
        user = users.get(username)
        print(f"Users dict: {users}")
        if user:
            print(f"Stored Password for {username}: {user['password']}")
            if user["password"] == hashed_password:
                print(f"User {username} authenticated successfully")
                return jsonify({"message": f"Welcome, {username}!", "redirect": url_for('home')})
            else:
                print(f"Password mismatch for user {username}")
        else:
            print(f"User {username} not found")
        return jsonify({"message": "Invalid username or password."}), 400

    return jsonify({"message": "No image data or credentials received."}), 400

if __name__ == '__main__':
    app.run(debug=True)
