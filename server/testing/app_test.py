# server/testing/app_test.py

from datetime import datetime, UTC
from app import app, db
from models import Message

import pytest

@pytest.fixture(autouse=True)
def clear_db():
    with app.app_context():
        Message.query.delete()
        db.session.commit()

def test_has_correct_columns():
    with app.app_context():
        msg = Message(
            body="Hello 👋",
            username="Liza",
            updated_at=datetime.now(UTC)
        )
        db.session.add(msg)
        db.session.commit()

        assert msg.body == "Hello 👋"
        assert msg.username == "Liza"
        assert isinstance(msg.created_at, datetime)

def test_returns_list_of_json_objects_for_all_messages_in_database():
    with app.app_context():
        msg1 = Message(body="Hello 👋", username="Liza", updated_at=datetime.now(UTC))
        db.session.add(msg1)
        db.session.commit()

        response = app.test_client().get("/messages")
        assert response.status_code == 200
        records = Message.query.all()

        for message in response.json:
            assert message['id'] in [record.id for record in records]
            assert message['body'] in [record.body for record in records]

def test_creates_new_message_in_the_database():
    with app.app_context():
        response = app.test_client().post(
            "/messages",
            json={"body": "Hello 👋", "username": "Liza"},
        )

        assert response.status_code == 201
        h = Message.query.filter_by(body="Hello 👋").first()
        assert h

def test_returns_data_for_newly_created_message_as_json():
    with app.app_context():
        response = app.test_client().post(
            "/messages",
            json={"body": "Hello 👋", "username": "Liza"},
        )

        assert response.status_code == 201
        assert response.content_type == "application/json"
        assert response.json["body"] == "Hello 👋"
        assert response.json["username"] == "Liza"

def test_updates_body_of_message_in_database():
    with app.app_context():
        msg = Message(body="Old Text", username="Liza", updated_at=datetime.now(UTC))
        db.session.add(msg)
        db.session.commit()

        response = app.test_client().patch(
            f"/messages/{msg.id}",
            json={"body": "New Text"},
        )

        assert response.status_code == 200
        updated_msg = Message.query.get(msg.id)
        assert updated_msg.body == "New Text"

def test_returns_data_for_updated_message_as_json():
    with app.app_context():
        msg = Message(body="Before", username="Liza", updated_at=datetime.now(UTC))
        db.session.add(msg)
        db.session.commit()

        response = app.test_client().patch(
            f"/messages/{msg.id}",
            json={"body": "After"},
        )

        assert response.status_code == 200
        assert response.json["body"] == "After"

def test_deletes_message_from_database():
    with app.app_context():
        msg = Message(body="Delete Me", username="Liza", updated_at=datetime.now(UTC))
        db.session.add(msg)
        db.session.commit()

        response = app.test_client().delete(f"/messages/{msg.id}")
        assert response.status_code == 204

        assert not Message.query.get(msg.id)
