from models import User, Item
from extensions import db

def test_user_password_hashing(client):
    u = User(username="abc", email="abc@test.com")
    u.set_password("secret123")
    assert u.check_password("secret123")
    assert not u.check_password("wrong")

def test_create_item(client):
    item = Item(
        name="Test Product",
        description="demo",
        category="Electronics",
        quantity=5
    )
    db.session.add(item)
    db.session.commit()

    assert item.id is not None
