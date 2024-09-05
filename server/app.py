from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy()


db.init_app(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(250), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'username': self.username,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Create message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or not 'body' in data or not 'username' in data:
        return jsonify({"error": "Invalid input"}), 400

    new_message = Message(body=data['body'], username=data['username'])
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

# Get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    if not messages:
        return jsonify([])  # Return an empty list if no messages exist
    return jsonify([message.to_dict() for message in messages]), 200

# Update message
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
    db.session.commit()

    return jsonify(message.to_dict()), 200


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()

    return jsonify({"message": "Message deleted"}), 200
