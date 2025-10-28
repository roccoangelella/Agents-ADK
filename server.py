from fastmcp import FastMCP
import os
import hashlib
import pymupdf
from sentence_transformers import SentenceTransformer
from mongo import _mongo_client

mcp=FastMCP(
    name='My MCP Server'
)

def chunk_pdf(filename, chunk_size, overlap):
    doc=pymupdf.open(filename)
    text=""
    for page in doc:
        text+=page.get_text()
    chunks=[]
    start=0
    while start<len(text):
        chunks.append(text[start:start+chunk_size])
        start+=(chunk_size-overlap)
    return chunks

def embed_and_upload_pdf(chunks:list):
    """ A function that returns the content of one or more PDF files as a string, given the folder specified by the user. """    
    model=SentenceTransformer('all-MiniLM-L6-v2')
    docs=[]
    client=_mongo_client()
    db=client['vector-db']
    embeddings_coll=db['embeddings']
    ids=[hashlib.sha256(chunk.encode('utf-8')).hexdigest() for chunk in chunks]

        embeddings = model.encode(chunk)
        docs.append({'chunk_id':id,'embedding':embeddings.tolist()})
    

    embeddings_coll.insert_many(docs)
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
    


if __name__=='__main__':
    mcp.run(
        transport="streamable-http",
        port=8080,
        host="127.0.0.1",
        log_level="INFO"
    )