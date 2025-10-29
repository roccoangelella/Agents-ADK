from fastmcp import FastMCP
import os
import hashlib
import pymupdf
from sentence_transformers import SentenceTransformer
from utils.mongo import _mongo_client
from numpy import dot
from numpy.linalg import norm
import zlib
import base64
import textract

mcp=FastMCP(
    name='My MCP Server'
)

def chunk_text(file_path,chunk_size,overlap):
    try:
        text=textract.process(file_path).decode('utf-8')
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        text = ""
    chunks=[]
    start=0
    while start<len(text):
        chunks.append(text[start:start+chunk_size])
        start+=(chunk_size-overlap)
    print('Text Chunked\n---------')
    return chunks

def embed_and_upload_pdf(chunks:list):
    """ A function that returns the content of one or more PDF files as a string, given the folder specified by the user. """    
    model=SentenceTransformer('all-MiniLM-L6-v2')
    docs=[]
    client=_mongo_client()
    db=client['vector-db']
    embeddings_coll=db['embeddings']

    ids=[hashlib.sha256(chunk.encode('utf-8')).hexdigest() for chunk in chunks]
    existing_ids=[item['_id'] for item in embeddings_coll.find({'chunk_id':{'$in':ids}},{'_id':0,'chunk_id':1})]
    print('Ids Ok, for loop deciding which to upload')
    for id,chunk in zip(ids,chunks):
        if id not in existing_ids:
            chunk_bytes=chunk.encode('utf-8')
            compressed=zlib.compress(chunk_bytes)
            encoded=base64.b64encode(compressed).decode('ascii')
            
            embedding = model.encode(chunk)
            try:
                redundant_search=next(embeddings_coll.aggregate([
                    {"$vectorSearch":{
                        'index':'vector_index',
                        'path':'embedding',
                        'queryVector':embedding.tolist(),
                        'numCandidates':10,
                        'limit':1
                    }}
                ]))
            except StopIteration:
                redundant_search=None
            print(redundant_search)
            if not redundant_search or dot(embedding,redundant_search['embedding'])/(norm(embedding)*norm(redundant_search['embedding']))<=0.93:
                print('Cosine similarity lower than 0.93, appending.')
                docs.append({'chunk_encoded':encoded,'_id':id,'embedding':embedding.tolist()})
            else:
                print('Very high cosine similarity, rdundant chunk')
    if docs:
        embeddings_coll.insert_many(docs)
        print('New Embeddings uploaded to mongo')
    else:
        print('No new embeddings')
    client.close()

def embed_prompt_and_retrieve(prompt:str)->str:
    model=SentenceTransformer('all-MiniLM-L6-v2')
    prompt_embedding=model.encode(prompt).tolist()
    client=_mongo_client()
    db=client['vector-db']
    embeddings_coll=db['embeddings']
    vector_search=[
        {"$vectorSearch":{
            'index':'vector_index',
            'path':'embedding',
            'queryVector':prompt_embedding,
            'numCandidates':10,
            'limit':5

        }}
    ]
    result=list(embeddings_coll.aggregate(vector_search))
    client.close()
    return result

def scan_folder(folder):
    filenames=os.listdir(f'./{folder}')
    text=[]
    for file in filenames:
        curr_path=f"./{folder}/{file}"
        if os.path.isfile(curr_path):
            if file.endswith(('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')):
                print(f"Processing file: {curr_path}")
                text.append(chunk_text(curr_path,500,50))

        if os.path.isdir(curr_path):
            for dirpath,dirnames,files_in_subdir in os.walk(curr_path):
                for f_name in files_in_subdir:
                    if f_name.endswith(('.pdf','.txt','.doc','.docx','.epub','.odt','.pptx')):
                        full_file_path=os.path.join(dirpath, f_name)
                        print(f"Processing file in dir: {full_file_path}")
                        text.append(chunk_text(full_file_path,500,50))
    return text
    
if __name__=='__main__':
    mcp.run(
        transport="streamable-http",
        port=8080,
        host="127.0.0.1",
        log_level="INFO"
    )