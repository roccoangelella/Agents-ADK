import asyncio

from utils.rag import *
from utils.mongo import _mongo_client

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from sentence_transformers import SentenceTransformer

import time,os,threading

model=SentenceTransformer('all-MiniLM-L6-v2')
client=_mongo_client()

embeddings_coll=client['vector-db']['embeddings']

app=FastAPI()

class DocumentHandler(FileSystemEventHandler):
    def __init__(self,model,collection):
        self.model=model
        self.collection=collection
        self.valid_extensions=('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')
        self.loop=asyncio.new_event_loop()
    
    def on_created(self, event):
        if not event.is_directory:
            _,extension=os.path.splitext(event.src_path)
            if extension.lower() in self.valid_extensions:
                print(f'New file {event.src_path} detected')
                time.sleep(5)
                self.loop.run_until_complete(file_process(event.src_path,self.collection,self.model))
    
    def on_modified(self, event):
        if not event.is_directory:
            _,extension=os.path.splitext(event.src_path)
            if extension.lower() in self.valid_extensions:
                print(f'Modified file {event.src_path} detected')
                self.loop.run_until_complete(delete_file_chunks(event.src_path,self.collection))
                time.sleep(5)
                self.loop.run_until_complete(file_process(event.src_path,self.collection,self.model))
    
    def on_deleted(self, event):
        if not event.is_directory:
            print(f'Deleted file {event.src_path} detected')
            self.loop.run_until_complete(delete_file_chunks(event.src_path,self.collection))
    
def start_watcher(files_folder):
    if not os.path.exists(files_folder):
        print(f'{files_folder} folder not found. Creating it...')
        os.makedirs(files_folder)

    handler=DocumentHandler(model,embeddings_coll_async)
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
    scan_folder('./DOCS',embeddings_coll,model,('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')) 
    watcher_thread=threading.Thread(
        target=start_watcher,
        args=('./DOCS',),
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

if __name__=='__main__':
    print('Starting fastAPI server...')
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_excludes=['./DOCS']
    )