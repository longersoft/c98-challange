from flask import Flask, request, jsonify, g
import os
import hashlib
import sqlite3

app = Flask(__name__)


DATABASE = 'file_storage.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def calculate_file_hash(file_data):
    return hashlib.md5(file_data).hexdigest()


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    uploaded_file = request.files['file']
    file_name = uploaded_file.filename
    file_content = uploaded_file.read()
    file_hash = calculate_file_hash(file_content)

    cursor = get_db().cursor()
    cursor.execute("SELECT name FROM files WHERE content_hash=?", (file_hash,))
    existing_file = cursor.fetchone()
    if existing_file:
        return jsonify({'message': 'File already exists as ' + existing_file[0]})

    file_path = os.path.join('uploads', file_name)
    uploaded_file.save(file_path)

    cursor.execute(
        "INSERT INTO files (name, content_hash) VALUES (?, ?)", (file_name, file_hash))
    get_db().commit()

    return jsonify({'message': 'File uploaded successfully'}), 201


@app.route('/retrieve/<string:file_name>', methods=['GET'])
def retrieve_file(file_name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM files WHERE name=?", (file_name,))
    stored_file = cursor.fetchone()

    if not stored_file:
        cursor.close()
        return jsonify({'error': 'File not found'}), 404

    file_path = os.path.join('uploads', file_name)
    with open(file_path, 'rb') as file:
        file_content = file.read()

    cursor.close()
    return jsonify({'file_content': file_content.decode()}), 200


@app.route('/delete/<string:file_name>', methods=['DELETE'])
def delete_file(file_name):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM files WHERE name=?", (file_name,))
    stored_file = cursor.fetchone()

    if not stored_file:
        cursor.close()  # Close the cursor when done
        return jsonify({'error': 'File not found'}), 404

    file_path = os.path.join('uploads', file_name)
    os.remove(file_path)

    cursor.execute("DELETE FROM files WHERE name=?", (file_name,))
    db.commit()

    cursor.close()  # Close the cursor when done
    return jsonify({'message': 'File deleted successfully'}), 200


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
