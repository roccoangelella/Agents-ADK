import os
import hashlib
# from numpy import dot
# from numpy.linalg import norm
import zlib
import base64
import textract

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

def embed_and_upload_file(chunks:list,embeddings_coll,file_path:str,model):
    """ A function that returns the content of one or more PDF files as a string, given the folder specified by the user. """    

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

def retrieve(prompt:str,embeddings_coll,model)->str:
    prompt_embedding=model.encode(prompt).tolist()
    vector_search=[
        {"$vectorSearch":{
            'index':'vector_index',
            'path':'embedding',
            'queryVector':prompt_embedding,
            'numCandidates':10,
            'limit':5

        }}
    ]
    results=list(embeddings_coll.aggregate(vector_search))
    retrieved_chunks=""
    for result in results:
        retrieved_chunks+='\n'+zlib.decompress(base64.b64decode(result['chunk_encoded'])).decode('utf-8')
    return retrieved_chunks

def file_process(file_path:str,embeddings_coll,model):
    print(f"WATCHDOG: Processing file: {file_path}")
    chunks=chunk_text(file_path, 500, 50)
    if chunks:
        embed_and_upload_file(chunks,embeddings_coll,model,file_path)

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

                if full_path not in existing_files:
                    print(f"STARTUP: Found new file: {full_path}")
                    file_process(full_path,embeddings_coll,model)
    return text
    
def delete_file_chunks(file_path: str, embeddings_coll):
    """Removes all chunks associated with a specific file."""
    print(f"WATCHDOG: Deleting chunks for file: {file_path}")
    result=embeddings_coll.delete_many({'source_file':file_path})
    print(f"Deleted {result.deleted_count} chunks.")