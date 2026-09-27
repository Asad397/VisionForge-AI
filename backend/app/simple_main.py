from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI

app = FastAPI()

@app.get('/health')
def health():
    return {'status': 'ok'}
