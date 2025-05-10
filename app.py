from flask import Flask, request, jsonify
import face_recognition
import os

app = Flask(__name__)

known_encodings = []
known_names = []

# Load known faces from known_faces/<name>/<images>.jpg
def load_known_faces():
    base_dir = "known_faces"
    for person in os.listdir(base_dir):
        person_dir = os.path.join(base_dir, person)
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person)

load_known_faces()

@app.route('/verify-face', methods=['POST'])
def verify():
    if 'image' not in request.files:
        return jsonify({'match': False, 'error': 'No image uploaded'}), 400

    img = face_recognition.load_image_file(request.files['image'])
    encodings = face_recognition.face_encodings(img)

    if not encodings:
        return jsonify({'match': False, 'error': 'No face found'}), 200

    matches = face_recognition.compare_faces(known_encodings, encodings[0])
    if True in matches:
        idx = matches.index(True)
        return jsonify({'match': True, 'user': known_names[idx]})
    else:
        return jsonify({'match': False, 'error': 'No match'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
