import asyncio

from utils.rag import retrieve, file_process, delete_file_chunks, scan_folder
from utils.mongo import _mongo_client

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sentence_transformers import SentenceTransformer

import time
import os
import threading

model=SentenceTransformer('all-MiniLM-L6-v2')
client=_mongo_client()

embeddings_coll=client['vector-db']['embeddings']

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Message model
class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: Message):
    try:
        # Use your existing retrieve function
        response = retrieve(message.message, embeddings_coll, model)
        return {"response": response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

class DocumentHandler(FileSystemEventHandler):
    def __init__(self,model,collection):
        self.model=model
        self.collection=collection
        self.valid_extensions=('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')
    
    def on_created(self, event):
        if not event.is_directory:
            _,extension=os.path.splitext(event.src_path)
            if extension.lower() in self.valid_extensions:
                print(f'New file {event.src_path} detected')
                time.sleep(5)
                file_process(event.src_path,self.collection,self.model)
    
    def on_modified(self, event):
        if not event.is_directory:
            _,extension=os.path.splitext(event.src_path)
            if extension.lower() in self.valid_extensions:
                print(f'Modified file {event.src_path} detected')
                delete_file_chunks(event.src_path, self.collection)
                time.sleep(5)
                file_process(event.src_path,self.collection,self.model)
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f'Deleted file {event.src_path} detected')
            delete_file_chunks(event.src_path, self.collection)

def start_watcher(files_folder):
    if not os.path.exists(files_folder):
        print(f'{files_folder} folder not found. Creating it...')
        os.makedirs(files_folder)

    handler=DocumentHandler(model,embeddings_coll)
    observer=Observer()
    observer.schedule(handler,path=files_folder,recursive=True)
    observer.start()

    print(f'{files_folder} is now monitored') 
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

@app.on_event('startup')
def on_startup():
    scan_folder('DOCS',embeddings_coll,model,('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')) 
    watcher_thread=threading.Thread(
        target=start_watcher,
        args=('DOCS',),
        daemon=True
    )    
    watcher_thread.start()

@app.on_event('shutdown')
def on_shutdown():
    client.close()

@app.post('/query')  
def api_retrieve(query):
    retrieved=retrieve(query,embeddings_coll,model)
    return {'context':retrieved}

#uvicorn backend_fastapi.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude ./DOCS