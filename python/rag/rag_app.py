import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import chromadb
from langchain_ibm import WatsonxLLM
from langchain_huggingface import HuggingFaceEmbeddings

# Load env
load_dotenv()

# Initialize watsonx LLM
parameters = {
    "decoding_method": "greedy",
    "max_new_tokens": 1000,
    "min_new_tokens": 1,
}
llm = WatsonxLLM(
    model_id="meta-llama/llama-3-3-70b-instruct",
    url=os.getenv("WATSONX_URL"),
    project_id=os.getenv("WATSONX_PROJECT_ID"),
    apikey=os.getenv("WATSONX_API_KEY"),
    params=parameters,
)

# Init HuggingFace embeddings
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Init persistent ChromaDB
client = chromadb.PersistentClient(path="./chroma_store")

collection_name = "rag_pdf"
existing = [c.name for c in client.list_collections()]

if collection_name in existing:
    collection = client.get_collection(collection_name)
else:
    collection = client.create_collection(collection_name)


# Helper: Read PDF
def load_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


# Helper: Split text
def split_text(text, chunk_size=500):
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


# Add PDF chunks with embeddings
def add_pdf_to_chroma(path):
    pdf_text = load_pdf(path)
    chunks = split_text(pdf_text)
    for i, chunk in enumerate(chunks):
        embedding = embedder.embed_documents([chunk])[0]
        collection.add(documents=[chunk], embeddings=[embedding], ids=[str(i)])


# Retrieve relevant context
def retrieve_context(query, k=3):
    query_embedding = embedder.embed_query(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=k)
    contexts = results["documents"][0]
    return "\n".join(contexts)


# RAG flow
def rag_ask(query):
    context = retrieve_context(query)
    prompt = f"""You are an AI assistant. Use the context below to answer the question.

Context:
{context}

Question: {query}
Answer:"""
    return llm.invoke(prompt)


# MAIN
if __name__ == "__main__":

    # Step 1: Load the PDF file into the Chroma vector store
    add_pdf_to_chroma("sample.pdf")

    # Step 2: Ask a question about the content
    user_query = "What is Watsonx.ai and what does it provide?"
    answer = rag_ask(user_query)
    print("\nAnswer:\n", answer)
