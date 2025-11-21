"""
chain.py — FlightLens RAG Chain
Uses:
- MPNet embeddings (from FAISS index)
- Local HuggingFace generation model (FLAN-T5)
- FAISS retriever
"""

import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

load_dotenv()

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
INDEX_DIR = os.getenv("FAISS_INDEX_PATH", "models/faiss_index")
EMBED_MODEL = os.getenv("FLIGHTLENS_EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
LLM_MODEL = os.getenv("FLIGHTLENS_LLM_MODEL", "google/flan-t5-base")


# -------------------------------------------------------------------
# Load RAG Chain
# -------------------------------------------------------------------
def get_chain():
    """Initialize the Retrieval-Augmented Generation (RAG) chain."""

    print(f"Loading embeddings: {EMBED_MODEL}")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    print(f"Loading FAISS index from: {INDEX_DIR}")
    db = FAISS.load_local(
        INDEX_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    print(f"Loading LLM model: {LLM_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(LLM_MODEL)

    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=512
    )

    llm = HuggingFacePipeline(pipeline=pipe)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    return chain


# -------------------------------------------------------------------
# Main QA Functions
# -------------------------------------------------------------------
def answer_question(query: str) -> str:
    """Basic RAG answer only."""
    try:
        chain = get_chain()
        result = chain.invoke({"query": query})
        return result["result"]
    except Exception as e:
        return f"Error: {str(e)}"


def answer_question_with_sources(query: str):
    """Return answer + top source chunks."""
    try:
        chain = get_chain()
        retriever = chain.retriever

        docs = retriever.get_relevant_documents(query)
        result = chain.invoke({"query": query})
        answer = result["result"]

        sources = []
        for doc in docs:
            sources.append({
                "content": doc.page_content[:300] + "...",
                "metadata": doc.metadata
            })

        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }

    except Exception as e:
        return {"answer": f"Error: {e}", "sources": [], "num_sources": 0}


# -------------------------------------------------------------------
# Test
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("\nTesting RAG chain with MPNet embeddings...\n")
    query = "What are the steps for engine fire during flight?"
    response = answer_question(query)
    print("Q:", query)
    print("A:", response)
