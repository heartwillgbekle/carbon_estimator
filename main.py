
import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

ENERGY_PER_GB_KWH = 0.81
GLOBAL_GRID_INTENSITY_GCO2E_PER_KWH = 442 
CEREBRAS_MODEL = "btlm-3b-8k-base"

app = FastAPI(
    title="Carbon Estimation API",
    description="An API to estimate the digital carbon footprint of a website.",
    version="1.0.0"
)

class WebsiteInput(BaseModel):
    monthly_visits: int = Field(..., gt=0, description="Total monthly visits to the website.")
    data_per_visit_mb: float = Field(..., gt=0, description="Data transferred per average visit in Megabytes (MB).")

class OrganizationInput(BaseModel):
    name: str = Field(..., description="The name of the organization or website.")


def calculate_footprint(data: WebsiteInput):
    """A reusable function to perform the core carbon calculation."""
    data_per_visit_gb = data.data_per_visit_mb / 1024
    total_data_gb_yearly = data_per_visit_gb * data.monthly_visits * 12
    total_energy_kwh_yearly = total_data_gb_yearly * ENERGY_PER_GB_KWH
    total_carbon_g_yearly = total_energy_kwh_yearly * GLOBAL_GRID_INTENSITY_GCO2E_PER_KWH
    total_carbon_kg_yearly = total_carbon_g_yearly / 1000
    trees_equivalent = total_carbon_kg_yearly / 21

    return {
        "annual_footprint_kg_co2e": round(total_carbon_kg_yearly, 2),
        "equivalent_trees_to_offset": round(trees_equivalent, 2),
        "parameters": data.dict()
    }


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Carbon Estimation API!"}

@app.post("/v1/estimate")
def estimate_direct(data: WebsiteInput):
    """Estimates footprint directly from user-provided traffic data."""
    result = calculate_footprint(data)
    result["estimation_method"] = "Direct Calculation"
    return result

@app.post("/v1/estimate-by-name")
def estimate_by_organization_name(org_input: OrganizationInput):
    """
    Estimates footprint by first using the Cerebras LLM OR a mock response.
    """
    if os.getenv("MOCK_AI") == "True":
        mock_llm_output = {
            "monthly_visits": 5000000,
            "data_per_visit_mb": 2.5
        }
        website_data = WebsiteInput(**mock_llm_output)
        final_estimate = calculate_footprint(website_data)
        final_estimate["estimation_method"] = f"AI-Generated Inputs (MOCKED for {org_input.name})"
        return final_estimate

    if not CEREBRAS_API_KEY:
        raise HTTPException(status_code=500, detail="Cerebras API key not configured.")