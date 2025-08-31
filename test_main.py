from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_countries():
    """
    Test that the /countries endpoint returns the expected list of countries.
    Edge case: Ensure no extra or missing countries.
    """
    response = client.get("/countries")
    assert response.status_code == 200
    assert sorted(response.json()) == ["England", "France", "Germany", "Italy", "Peru", "Portugal", "Spain"]

def test_cities_spain():
    """
    Test that /countries/Spain/cities returns only the cities available for Spain.
    Edge case: Only 'Seville' should be present if that's the only city in weather.json.
    """
    response = client.get("/countries/Spain/cities")
    assert response.status_code == 200
    assert response.json() == ["Seville"]

def test_cities_invalid_country():
    """
    Test that requesting cities for a non-existent country returns a 404 error.
    Edge case: Country does not exist in the dataset.
    """
    response = client.get("/countries/Narnia/cities")
    assert response.status_code == 404

def test_monthly_average_valid():
    """
    Test that /countries/Spain/Seville/January returns valid weather data.
    Edge case: Valid country, city, and month.
    """
    response = client.get("/countries/Spain/Seville/January")
    assert response.status_code == 200
    # Check that the response contains expected keys (e.g., temperature, rainfall)
    assert isinstance(response.json(), dict)
    assert "temperature" in response.json() or "rainfall" in response.json()

def test_monthly_average_invalid_city():
    """
    Test that requesting weather data for a non-existent city returns a 404 error.
    Edge case: City does not exist in the country.
    """
    response = client.get("/countries/Spain/Madrid/January")
    assert response.status_code == 404

def test_monthly_average_invalid_month():
    """
    Test that requesting weather data for an invalid month returns a 404 error.
    Edge case: Month does not exist for the city.
    """
    response = client.get("/countries/Spain/Seville/NotAMonth")
    assert response.status_code == 404