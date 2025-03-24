import os
import pickle
from typing import List
import faiss
from sentence_transformers import SentenceTransformer

def embed_sentences(sentences: List[str], model) -> List[List[float]]:
    return model.encode(sentences)

#embeddings: [emb,]
def save_to_faiss(embeddings, sentences, index_file):
    try:
        dimension = embeddings.shape[1]
        if os.path.exists(index_file):
            with open(index_file, 'rb') as f:
                index, existing_sentences = pickle.load(f)
            
            if index.d != dimension:
                raise ValueError("The dimension of the existing index is inconsistent with the dimension of the new embedded vector")
            
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            
            existing_sentences.extend(sentences)
        else:
            index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            index.add(embeddings)
            existing_sentences = sentences
        
        with open(index_file, 'wb') as f:
            pickle.dump((index, existing_sentences), f)
        
    except Exception as e:
        print(f"{e}")

def load_faiss_index(index_file='faiss_index.bin'):
    with open(index_file, 'rb') as f:
        index, sentences = pickle.load(f)
    return index, sentences

def search(query: str, index, sentences, model, top_k: int = 5):
    query_embedding = model.encode([query])
    faiss.normalize_L2(query_embedding)  
    _, indices = index.search(query_embedding, top_k)  

    valid_indices = [i for i in indices[0] if i != -1]
    return [sentences[i] for i in valid_indices]

def index_text(index_text, doc_text, model,index_path='faiss_index.bin'):  
    embeddings = embed_sentences([index_text], model)
    save_to_faiss(embeddings, [doc_text], index_path)

def query(user_query, top_k, model, db_path="faiss_index.bin"):
    index, sentences = load_faiss_index(db_path)
    return search(user_query, index, sentences, model, top_k)

if __name__ == "__main__":
    embed_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device="cuda:1")
    print(query("test", 10, embed_model))
