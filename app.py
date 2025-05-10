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

            # Skip non-image files
            if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            try:
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    known_encodings.append(encodings[0])
                    known_names.append(person)
            except Exception as e:
                print(f"⚠️ Skipped file {img_path}: {e}")

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
    
    
@app.route('/register-face', methods=['POST'])
def register_face():
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'success': False, 'error': 'Image and name required'}), 400

    name = request.form['name']
    image_file = request.files['image']
    folder = os.path.join('known_faces', name)
    os.makedirs(folder, exist_ok=True)

    save_path = os.path.join(folder, image_file.filename)
    image_file.save(save_path)

    # Refresh known encodings
    known_encodings.clear()
    known_names.clear()
    load_known_faces()
    


    return jsonify({'success': True, 'message': f'Registered {name}'}), 200  


@app.route('/face/<user_id>', methods=['DELETE'])
def delete_face(user_id):
    user_dir = os.path.join('known_faces', user_id)

    if not os.path.exists(user_dir):
        return jsonify({'success': False, 'error': 'User not found'}), 404

    for file in os.listdir(user_dir):
        os.remove(os.path.join(user_dir, file))
    os.rmdir(user_dir)

    # Refresh encodings
    known_encodings.clear()
    known_names.clear()
    load_known_faces()

    return jsonify({'success': True, 'message': f'Face data for {user_id} deleted'}), 200
  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
