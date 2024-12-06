import cv2
import face_recognition
import os
import pickle

ENCODING_DIR = 'registered_faces'

def save_face_encoding(username, encoding):
    """Saves a face encoding with the user's username."""
    if not os.path.exists(ENCODING_DIR):
        os.makedirs(ENCODING_DIR)
    with open(f'{ENCODING_DIR}/{username}.pkl', 'wb') as f:
        pickle.dump(encoding, f)
    print(f"Saved encoding for {username}")

def capture_face_from_image(img, username):
    """Processes an image for face registration."""
    encoding = face_recognition.face_encodings(img)
    if encoding:
        save_face_encoding(username, encoding[0])
        return True
    print("No face found for registration.")
    return False

def authenticate_user_from_image(img):
    """Authenticates user based on the face in the image."""
    encoding = face_recognition.face_encodings(img)
    if not encoding:
        print("No face found in the provided image for authentication.")
        return None

    print(f"Encoding from provided image: {encoding[0]}")

    # Load all registered encodings
    registered_users = []
    for filename in os.listdir(ENCODING_DIR):
        if filename.endswith('.pkl'):
            with open(os.path.join(ENCODING_DIR, filename), 'rb') as f:
                registered_users.append((filename[:-4], pickle.load(f)))  # (username, encoding)

    # Compare the captured face with registered faces
    for username, registered_encoding in registered_users:
        matches = face_recognition.compare_faces([registered_encoding], encoding[0])
        print(f"Comparing with {username}: {matches}")
        if True in matches:
            print(f"Face recognized for user: {username}")
            return username

    print("No matching face found.")
    return None
