import shelve
from copy import deepcopy

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

DATABASE_PATH = './db_data/configs'

app = FastAPI()


class Integration(BaseModel):
    company_id: str
    data: dict


@app.post("/integration_configs/{integration_name}/{integration_id}")
async def post_config(
    integration_name: str,
    integration_id: str,
    integration: Integration,
) -> None:
    with shelve.open(DATABASE_PATH) as db:
        company_data = deepcopy(db[integration.company_id]) if db.get(integration.company_id) else {}
        company_data[integration_name] = {
            'integration_id': integration_id,
            'data': integration.data,
        }
        db[integration.company_id] = company_data


@app.delete("/integration_configs/{integration_name}/{integration_id}")
async def delete_config(
    integration_name: str,
    integration_id: str,
) -> None:
    with shelve.open(DATABASE_PATH) as db:
        for company_id, integrations in db.items():
            if (integration := integrations.get(integration_name)) and integration['integration_id'] == integration_id:
                new_integrations = deepcopy(integrations)
                new_integrations.pop(integration_name)
                db[company_id] = new_integrations
                return
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/integration_configs/{integration_name}/{integration_id}")
async def retrive_config(
    integration_name: str,
    integration_id: str,
) -> Integration:
    with shelve.open(DATABASE_PATH) as db:
        for company_id, integrations in db.items():
            if (integration := integrations.get(integration_name)) and integration['integration_id'] == integration_id:
                return {'company_id': company_id, **integration}

    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")
