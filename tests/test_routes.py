def test_home_page(client):
    # Must redirect to login because home has @login_required
    response = client.get('/', follow_redirects=True)
    assert b"Se connecter" in response.data


def test_dashboard_requires_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b"Se connecter" in response.data
