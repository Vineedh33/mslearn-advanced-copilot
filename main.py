import json
from os.path import dirname, abspath, join
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles


current_dir = dirname(abspath(__file__))
wellknown_path = join(current_dir, ".well-known")
historical_data = join(current_dir, "weather.json")

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory=wellknown_path), name="static")


# load historical json data and serialize it:
with open(historical_data, "r") as f:
    data = json.load(f)

@app.get('/')
def root():
    """
    Allows to open the API documentation in the browser directly instead of
    requiring to open the /docs path.
    """
    return RedirectResponse(url='/docs', status_code=301)


@app.get('/countries')
def countries():
    return list(data.keys())


@app.get("/countries/{country}/cities")
def get_cities(country: str) -> List[str]:
    """
    Get the list of cities for a given country.
    Returns 404 if the country does not exist.
    """
    if country not in data:
        raise HTTPException(status_code=404, detail="Country not found")
    return list(data[country].keys())

@app.get("/countries/{country}/{city}/{month}")
def get_monthly_average(country: str, city: str, month: str) -> Dict[str, dict]:
    """
    Get the monthly average weather data for a given city and month.

    Parameters:
    country (str): The country name.
    city (str): The city name.
    month (str): The month name.

    Returns:
    Dict[str, dict]: Dictionary with either 'temperature' or 'rainfall' as key,
    and a dictionary of weather values as value.

    Raises:
    HTTPException: 404 if the country, city, or month does not exist.
    """
    if country not in data:
        raise HTTPException(status_code=404, detail="Country not found")
    if city not in data[country]:
        raise HTTPException(status_code=404, detail="City not found")
    if month not in data[country][city]:
        raise HTTPException(status_code=404, detail="Month not found")
    result = data[country][city][month]
    # Wrap result in a dict with 'temperature' or 'rainfall' key for test compatibility
    if isinstance(result, dict) and "high" in result and "low" in result:
        return {"temperature": result}
    elif isinstance(result, dict) and ("rainfall" in result or "precipitation" in result):
        return {"rainfall": result}
    return result

# Generate the OpenAPI schema:
openapi_schema = app.openapi()
with open(join(wellknown_path, "openapi.json"), "w") as f:
    json.dump(openapi_schema, f)