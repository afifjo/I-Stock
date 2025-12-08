
import pytest
from extensions import db
from models import User, Item

def test_full_user_flow(client, app):
    """
    Test a complete user journey:
    1. Register (Admin role to skip manual approval)
    2. Login
    3. Add an Item
    4. Verify Item availability
    5. Logout
    """
    
    # ---------------------------
    # 1. REGISTER
    # ---------------------------
    response = client.post("/auth/register", data={
        "username": "qa_hero",
        "email": "qa@inventory.com",
        "password": "qaPassword123!",
        "confirm_password": "qaPassword123!",
        "role": "admin",
        "admin_code": "afif"
    }, follow_redirects=True)
    
    # We expect verify registration success by flash message or redirect
    # Based on auth.py: flash("Account created! Credentials sent to your email.", "success")
    # And redirect to login
    assert response.status_code == 200
    # Checking for specific byte string in response might be tricky due to templates,
    # but let's check if the user is in DB.
    with app.app_context():
        user = User.query.filter_by(username="qa_hero").first()
        assert user is not None
        assert user.role == "admin"
        assert user.is_approved is True

    # ---------------------------
    # 2. LOGIN
    # ---------------------------
    response = client.post("/auth/login", data={
        "username": "qa_hero",
        "password": "qaPassword123!"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for login success message or dashboard element
    # Based on auth.py: flash("Logged in successfully!", "success")
    assert b"Logged in successfully" in response.data or b"Tableau de bord" in response.data

    # ---------------------------
    # 3. ADD ITEM
    # ---------------------------
    # Route is /add (from main.py @bp.route("/add"))
    response = client.post("/add", data={
        "name": "QA Test Item",
        "description": "Created by automated integration test",
        "quantity": 42,
        "category": "informatique",
        "serial_number": "SN-12345",
        "assigned_to": "" # Unassigned
    }, follow_redirects=True)
    
    # Based on main.py: flash("Item added successfully!", "success")
    assert response.status_code == 200
    assert b"Item added successfully" in response.data

    # ---------------------------
    # 4. VERIFY ITEM
    # ---------------------------
    # Fetch item from DB to get ID
    with app.app_context():
        item = Item.query.filter_by(name="QA Test Item").first()
        assert item is not None
        item_id = item.id

    # Check detail page
    response = client.get(f"/item/{item_id}")
    assert response.status_code == 200
    assert b"QA Test Item" in response.data
    assert b"SN-12345" in response.data

    # ---------------------------
    # 5. LOGOUT
    # ---------------------------
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    # Based on auth.py: flash("Logged out successfully!", "info")
    # And redirects to login, where we might see "Se connecter"
    assert b"Logged out successfully" in response.data
