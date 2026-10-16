import uvicorn
from .api import app

if __name__ == "__main__":
    uvicorn.run("fridge.main:app", host="0.0.0.0", port=8787, reload=True)
