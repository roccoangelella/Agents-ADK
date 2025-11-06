import os
import hashlib
# from numpy import dot
# from numpy.linalg import norm
import zlib
import base64
import textract
from utils.mongo import _mongo_client
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

def chunk_text(file_path,chunk_size,overlap):
    try:
        text=textract.process(file_path).decode('utf-8')
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        text=""
    splitter=RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " ", ""],  
    chunk_size=chunk_size,
    chunk_overlap=overlap)

    return splitter.split_text(text)


def embed_and_upload_file(chunks:list,embeddings_coll,file_path:str,model):
    """ A function that returns the content of one or more PDF files as a string, given the folder specified by the user. """    
    file_path = file_path.replace('\\', '/')
    docs=[]
    ids=[hashlib.sha256(chunk.encode('utf-8')).hexdigest() for chunk in chunks]
    existing_ids=[item['_id'] for item in embeddings_coll.find({'_id':{'$in':ids}},{'_id':1,'chunk_id':1})]
    print('Ids Ok, for loop deciding which to upload')
    for id,chunk in zip(ids,chunks):
        if id not in existing_ids:
            chunk_bytes=chunk.encode('utf-8')
            compressed=zlib.compress(chunk_bytes)
            encoded=base64.b64encode(compressed).decode('ascii')
            
            embedding = model.encode(chunk)
            # try:
            #     redundant_search=next(embeddings_coll.aggregate([
            #         {"$vectorSearch":{
            #             'index':'vector_index',
            #             'path':'embedding',
            #             'queryVector':embedding.tolist(),
            #             'numCandidates':10,
            #             'limit':1
            #         }}
            #     ]))
            # except StopIteration:
            #     redundant_search=None
            # if not redundant_search or dot(embedding,redundant_search['embedding'])/(norm(embedding)*norm(redundant_search['embedding']))<=0.85:
            #     print('Cosine similarity lower than 0.85, appending.')
            #     docs.append({'chunk_encoded':encoded,'_id':id,'embedding':embedding.tolist()})
            # else:
            #     print('Very high cosine similarity, rdundant chunk')

            docs.append({
                'chunk_encoded':encoded,
                '_id':id,
                'embedding':embedding.tolist(),
                'source_file':file_path  
            })

    if docs:
        embeddings_coll.insert_many(docs)
        print('New Embeddings uploaded to mongo')
    else:
        print('No new embeddings')

def retrieve(prompt: str, source_file: str|None=None) -> str:
    client = _mongo_client()
    embeddings_coll = client['vector-db']['embeddings']
    model = SentenceTransformer('all-MiniLM-L6-v2')
    prompt_embedding = model.encode(prompt).tolist()
    vector_search_stage = {
        "$vectorSearch": {
            'index': 'vector_index',
            'path': 'embedding',
            'queryVector': prompt_embedding,
            'numCandidates': 100,
            'limit': 5
        }
    }
    if source_file:
        vector_search_stage["$vectorSearch"]["filter"] = {
            "source_file": source_file
        }

    pipeline = [vector_search_stage]
    results = list(embeddings_coll.aggregate(pipeline))

    retrieved_chunks=""
    for result in results:
        if 'chunk_encoded' in result:
            try:
                decoded_chunk = zlib.decompress(base64.b64decode(result['chunk_encoded'])).decode('utf-8')
                retrieved_chunks += '\n' + decoded_chunk
            except (zlib.error, base64.binascii.Error, UnicodeDecodeError) as e:
                print(f"Error decoding chunk for result {result.get('_id')}: {e}")
        else:
            print(f"Result {result.get('_id')} missing 'chunk_encoded' field.")

    return retrieved_chunks

def file_process(file_path:str,embeddings_coll,model):
    file_path = file_path.replace('\\', '/')
    print(f"WATCHDOG: Processing file: {file_path}")
    chunks=chunk_text(file_path, 1000, 100)
    if chunks:
        embed_and_upload_file(chunks,embeddings_coll,file_path,model)

def scan_folder(folder,embeddings_coll,model,valid_extensions):
    try:
        existing_files = set(embeddings_coll.distinct('source_file'))
        print(f"Found {len(existing_files)} files already in DB.")
    except Exception as e:
        print(f"Could not get existing files, will process all. Error: {e}")
        existing_files = set()
    
    text=[]
    for dirpath,_,files in os.walk(folder):
            for f_name in files:
                if f_name.endswith(valid_extensions):
                    full_path = os.path.join(dirpath, f_name)
                    full_path = full_path.replace('\\', '/')    
                if full_path not in existing_files:
                    print(f"STARTUP: Found new file: {full_path}")
                    file_process(full_path,embeddings_coll,model)
    return text
    
def delete_file_chunks(file_path: str, embeddings_coll):
    """Removes all chunks associated with a specific file."""
    file_path = file_path.replace('\\', '/')
    print(f"WATCHDOG: Deleting chunks for file: {file_path}")
    result=embeddings_coll.delete_many({'source_file':file_path})
    print(f"Deleted {result.deleted_count} chunks.")