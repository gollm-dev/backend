import threading
from typing import Optional

import fastapi
from fastapi.responses import JSONResponse

import uvicorn
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from db import db
import helpers

app = fastapi.FastAPI(
    title="gollm",
    description="Host any LLM on golem network",
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelDownloadRequest(BaseModel):
    model_name: str


class CompletionRequest(BaseModel):
    model_name: str
    question: str
    context: Optional[str]


@app.post("/downloadModel")
async def initiate_model_download(model: ModelDownloadRequest):
    model_obj = db.models_statuses.find_one({"model_name": model.model_name})

    if model_obj and model_obj.get('status') == "downloading":
        return JSONResponse(content={"error": "Model download is already in progress."}, status_code=409)
    if model_obj and model_obj.get('status') == "downloaded":
        return JSONResponse(content={"error": "Model is already downloaded."}, status_code=409)

    threading.Thread(target=helpers.download_and_load_model, args=(model.model_name, helpers.MODEL_DIR)).start()
    return JSONResponse(content={"message": f"{model.model_name} downloading started."}, status_code=200)


@app.post("/downloadStatus")
async def download_status(model: ModelDownloadRequest):
    model_obj = db.models_statuses.find_one({"model_name": model.model_name})

    if not model_obj:
        return JSONResponse(content={"error": "Model name not found."}, status_code=404)
    else:
        return JSONResponse(content={"status": model_obj.get('status')}, status_code=200)


@app.post("/createCompletion")
async def create_completion(request: CompletionRequest):
    try:
        model_obj = db.models_statuses.find_one({"model_name": request.model_name})

        if not model_obj or (model_obj and model_obj.get('status') != 'downloaded'):
            return JSONResponse(
                content={"error": "Model is not ready. Ensure it is downloaded and not in progress."},
                status_code=400
            )

        qa_pipeline = helpers.models.models[request.model_name.replace('/', '-')].get("model")
        result = qa_pipeline(question=request.question, context=request.context)
        return result
    except Exception as e:
        helpers.log(f"Error in create_completion: {e}")

uvicorn.run(app, host="0.0.0.0", port=5000)
