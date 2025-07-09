from app import app
import pytest

@pytest.fixture
def client():
    """A test client for the app."""
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data  # Check expected content
    assert response.content_type == "text/html; charset=utf-8"  # Ensure HTML response

def test_transactions(client):
    """Test the transactions route."""
    response = client.get('/transactions')
    data = response.data.decode('utf-8')  # decode bytes to string for easier checks

    assert response.status_code == 200
    assert "Transactions" in data
    assert "Add transaction" in data or "Add Transaction" in data
    assert response.content_type == "text/html; charset=utf-8"

    # Detailed table checks
    assert "<table" in data and "</table>" in data, "Table tags not found"
    assert "<thead" in data and "</thead>" in data, "Table head section missing"
    assert "<tbody" in data and "</tbody>" in data, "Table body section missing"
    assert "<tr" in data, "No table rows found"
    assert ("Transaction ID" in data or "Date" in data or "Amount" in data), "Expected table headers not found"
    assert "<td" in data, "No table data cells found"

def test_reports(client):
    """Test the reports route."""
    response = client.get('/reports')
    assert response.status_code == 200
    assert b"Reports" in response.data  # Confirm page content
    assert response.content_type == "text/html; charset=utf-8"

def test_settings(client):
    """Test the settings route."""
    response = client.get('/settings')
    assert response.status_code == 200
    assert b"Settings" in response.data  # Confirm page content
    assert response.content_type == "text/html; charset=utf-8"
