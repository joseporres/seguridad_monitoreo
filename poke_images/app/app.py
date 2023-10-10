from fastapi import FastAPI,Request
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.config.settings import api_settings
import uvicorn
from fastapi.exceptions import HTTPException
from app.config.mongo import pokemons, logs
from fastapi.responses import JSONResponse
from datetime import datetime
from app.constants.values import LOG_API_PATHS
import os
import base64
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

    path = request.url.path
    log_request = any(path.startswith(api_path) for api_path in LOG_API_PATHS)
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

@app.get("/search/{name}")
# @log_request() 
def root(name : str):
    try:
        name = name.capitalize()
        images_directory = "app/images"
        folder_path = os.path.join(images_directory, name)
        print(folder_path)

        if not os.path.exists(folder_path):
            print("No existe")
            return HTTPException(status_code=404, detail="Pokemon not found")
        image_list = []
        # print(os.listdir(folder_path))
        for filename in os.listdir(folder_path):
            if filename.endswith((".jpg", ".png")):  # Filtra solo archivos de imagen
                with open(os.path.join(folder_path, filename), "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode("utf-8")
                    image_list.append({
                        "name": filename,
                        "data": image_data
                    })
        
        return JSONResponse(content=image_list, status_code=200)

           
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))




def run():
    uvicorn.run(app,
                host=api_settings.HOST,
                port=api_settings.PORT,
                )
