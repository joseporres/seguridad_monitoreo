from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.exceptions import HTTPException
from app.config.mongo import logs
from fastapi.responses import JSONResponse
from datetime import datetime
from app.constants.values import LOG_API_PATHS
import requests
import concurrent.futures


app = FastAPI(
    title=api_settings.TITLE,
    openapi_url=f'{api_settings.PREFIX}/openapi.json',
    docs_url=f'{api_settings.PREFIX}/docs',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# set prefix  all routes

app.router.prefix = api_settings.PREFIX


@app.middleware("http")
async def log_request(request: Request, call_next):

    path = request.url.path
    log_request = any(api_path in path for api_path in LOG_API_PATHS)
    if not log_request:
        return await call_next(request)

    start_time = datetime.now()

    # Antes de manejar la solicitud
    response = await call_next(request)

    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    # Insertar datos de registro en la colección "logs"
    log_entry = {
        "module": api_settings.TITLE,
        "method": request.method,
        "endpoint": path,
        "status_code": response.status_code,
        "execution_time": execution_time,
        "timestamp": start_time,
    }
    logs.insert_one(log_entry)

    return response


@app.get("/")
def root():
    return {"message": f"Welcome to {api_settings.TITLE}"}


def fetch_data(api_url):
    response = requests.get(api_url)
    return response.json()


@app.get("/search/{name}")
# @log_request()
def root(name: str):
    try:
        name = name.lower()

        api_urls = [
            f'{api_settings.API_GATEWAY}poke_api/search/{name}',
            f'{api_settings.API_GATEWAY}poke_stats/search/{name}',
            f'{api_settings.API_GATEWAY}poke_images/search/{name}',
        ]
        # print(api_urls)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_data, api_urls))

        return {"data": results}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
