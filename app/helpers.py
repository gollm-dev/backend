import os
import requests
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

import config
from db import db as sync_db

# Directory to store models
MODEL_DIR = "./models"
STATUS_FILE = "./model_statuses.json"

# Ensure the model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)


class Models:
    def __init__(self):
        self.models = {}
        self._load_all()

    def add_model(self, model_name, model):
        self.models[model_name] = {'model': model}

    def _load_all(self):
        loaded_models = list(sync_db.models_statuses.find({'status': 'downloaded'}))
        for model in loaded_models:
            try:
                model['model_name'] = model['model_name'].replace('/', '-')
                self.add_model(
                    model['model_name'],
                    pipeline(
                        "question-answering",
                        model=os.path.join(MODEL_DIR, model['model_name']),
                        tokenizer=os.path.join(MODEL_DIR, model['model_name'])
                    )
                )
            except: pass


models = Models()


def log(message):
    """Logging function"""
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.get(url, params={'chat_id': config.TELEGRAM_LOGS_CHANNEL, 'text': message})
        print(message)
    except Exception as e:
        print(f"Error in logging: {e}")


def download_and_load_model(model_name, model_dir):
    """Downloading model"""

    try:
        model_path = os.path.join(model_dir, model_name.replace('/', '-'))
        # Check if the model directory exists to determine if the model has already been downloaded
        if os.path.exists(model_path):
            return
        # If not, create the directory and start the download process
        os.makedirs(model_path, exist_ok=True)
        # Update the status to reflect that the download is in progress
        sync_db.models_statuses.update_one(
            {"model_name": model_name},
            {"$set": {"status": "downloading"}},
            upsert=True
        )

        # Download and save the model and tokenizer
        model = AutoModelForQuestionAnswering.from_pretrained(model_name, cache_dir=model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_path)
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)

        # Update the status to reflect that the download is complete
        sync_db.models_statuses.update_one(
            {"model_name": model_name},
            {"$set": {"status": "downloaded", "model_path": model_path}},
            upsert=True
        )
        models.add_model(
            model_name.replace('/', '-'),
            pipeline("question-answering", model=model_path, tokenizer=model_path)
        )

    except Exception as e:
        log(f'Error in downloading model {model_name}: {e}')
