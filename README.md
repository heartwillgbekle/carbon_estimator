# carbon_estimator
# Carbon Estimation API

This service estimates the digital carbon footprint of a website.

## How to Run

1.  Create a virtual environment: `python3 -m venv venv`
2.  Activate it: `source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt`
4.  Create a `.env` file and add `MOCK_AI=True`.
5.  Run the server: `uvicorn main:app --reload`

## Endpoints

-   `POST /v1/estimate-by-name`: Estimates footprint using a (currently mocked) AI to find inputs.
