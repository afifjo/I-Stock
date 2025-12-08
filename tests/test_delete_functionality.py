from models import User, Item, Staff
from extensions import db
import datetime

def test_delete_item(client):
    # 1. Create and Login User
    with client.application.app_context():
        user = User(username="deleter", email="delete@example.com", is_approved=True)
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    client.post('/auth/login', data={
        "username": "deleter",
        "password": "pass"
    }, follow_redirects=True)

    # 2. Add an Item directly to DB
    with client.application.app_context():
        item = Item(
            name="Delete Me Item",
            quantity=10,
            user_id=user_id,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    # 3. Simulate correct POST request to delete
    # The route is /delete/<item_id> (POST)
    response = client.post(f'/delete/{item_id}', follow_redirects=True)
    
    # 4. Assertions
    assert response.status_code == 200
    # Flash message content may change; DB state is the critical check
    
    # Verify DB
    with client.application.app_context():
        deleted_item = Item.query.get(item_id)
        assert deleted_item is None

def test_delete_staff(client):
    # 1. Create and Login User
    with client.application.app_context():
        user = User(username="staff_deleter", email="staff_del@example.com", is_approved=True)
        user.set_password("pass")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    client.post('/auth/login', data={
        "username": "staff_deleter",
        "password": "pass"
    }, follow_redirects=True)

    # 2. Add a Staff directly to DB
    with client.application.app_context():
        staff = Staff(
            name="Delete Me Staff",
            email="staff@delete.com",
            user_id=user_id
        )
        db.session.add(staff)
        db.session.commit()
        staff_id = staff.id

    # 3. Simulate correct POST request to delete 
    # The route is /staff/delete/<staff_id> (POST)
    response = client.post(f'/staff/delete/{staff_id}', follow_redirects=True)

    # 4. Assertions
    assert response.status_code == 200
    # Flash message content may change; DB state is the critical check

    # Verify DB
    with client.application.app_context():
        deleted_staff = Staff.query.get(staff_id)
        assert deleted_staff is None
