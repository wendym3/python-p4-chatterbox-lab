from datetime import datetime
from app import app, db, Message

class TestApp:
    '''Flask application test cases'''

    def setup_method(self):
        '''Create app context and ensure a clean database'''
        with app.app_context():
            db.drop_all()
            db.create_all()

    def teardown_method(self):
        '''Tear down the app context and clean up the database'''
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_has_correct_columns(self):
        with app.app_context():
            message = Message(body="Hello 👋", username="Liza")
            db.session.add(message)
            db.session.commit()

            assert message.body == "Hello 👋"
            assert message.username == "Liza"
            assert type(message.created_at) == datetime

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        with app.app_context():
            message1 = Message(body="Hello 👋", username="Liza")
            message2 = Message(body="Goodbye 👋", username="Tom")
            db.session.add_all([message1, message2])
            db.session.commit()

            response = app.test_client().get('/messages')
            assert response.status_code == 200

            records = Message.query.all()
            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={"body": "Hello 👋", "username": "Liza"}
            )

            assert response.status_code == 201
            h = Message.query.filter_by(body="Hello 👋").first()
            assert h

    def test_returns_data_for_newly_created_message_as_json(self):
        with app.app_context():
            response = app.test_client().post(
                '/messages',
                json={"body": "Hello 👋", "username": "Liza"}
            )

            assert response.content_type == 'application/json'
            assert response.status_code == 201
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

    def test_updates_body_of_message_in_database(self):
        with app.app_context():
            message = Message(body="Hello 👋", username="Liza")
            db.session.add(message)
            db.session.commit()

            response = app.test_client().patch(
                f'/messages/{message.id}',
                json={"body": "Goodbye 👋"}
            )

            assert response.status_code == 200
            assert response.json['body'] == "Goodbye 👋"

    def test_returns_data_for_updated_message_as_json(self):
        with app.app_context():
            message = Message(body="Hello 👋", username="Liza")
            db.session.add(message)
            db.session.commit()

            response = app.test_client().patch(
                f'/messages/{message.id}',
                json={"body": "Goodbye 👋"}
            )

            assert response.content_type == 'application/json'
            assert response.status_code == 200
            assert response.json["body"] == "Goodbye 👋"

    def test_deletes_message_from_database(self):
        with app.app_context():
            message = Message(body="Hello 👋", username="Liza")
            db.session.add(message)
            db.session.commit()

            response = app.test_client().delete(f'/messages/{message.id}')
            assert response.status_code == 200

            deleted_message = Message.query.filter_by(id=message.id).first()
            assert deleted_message is None
