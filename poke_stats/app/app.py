from fastapi import FastAPI,Request
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.exceptions import HTTPException
from app.config.mongo import pokemons, logs
from fastapi.responses import JSONResponse
from datetime import datetime
# import time

app = FastAPI(
    title=api_settings.TITLE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = datetime.now()
    
    # Antes de manejar la solicitud
    response = await call_next(request)
    
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    # Insertar datos de registro en la colección "logs"
    log_entry = {
        "method": request.method,
        "endpoint": request.url.path,
        "status_code": response.status_code,
        "execution_time": execution_time,
        "timestamp": start_time,
    }
    logs.insert_one(log_entry)

    return response

@app.get("/{name}")
# @log_request() 
def root(name : str):
    try:
        foundPokemon = pokemons.find_one({"Name": name})
        if foundPokemon:
           foundPokemon['_id'] = str(foundPokemon['_id'])
           return JSONResponse(content=foundPokemon, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))




def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
