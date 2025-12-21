from langchain.tools import tool, ToolRuntime
from graphs.axelle_ai.src.config import tavily_client, TRUSTED_DOMAINS
from graphs.axelle_ai.src.contexts import Context
from typing import Literal



@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return "Ghana" if user_id == "1" else "Europe"
@tool
# Search tool to use to do research
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance" ] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    search_docs = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
        #add trusted domains
        #trusted_domains=TRUSTED_DOMAINS,
    )
    return search_docs

@tool
def get_date():
    """Get the current date."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

@tool
def search_medical_docs(query: str) -> str:
    """Search the AxelleMedicalDocs Weaviate collection for relevant medical documents.
    
    Use this to find medical information based on patient symptoms, conditions, or treatments.
    
    Args:
        query: Search query (e.g., "treatment for breast cancer")
    
    Returns formatted results with sources.
    """
    # Set default values internally
    k = 7
    alpha = 0.0
    from langchain_weaviate import WeaviateVectorStore
    import weaviate
    from graphs.axelle_ai.src.config import EMBEDDING_MODEL
    # Initialize client and store (reuse connection)
    weaviate_client = weaviate.connect_to_local(port=8001)
    embeddings = EMBEDDING_MODEL
    
    try:
        store = WeaviateVectorStore(
            client=weaviate_client,
            index_name="AxelleMedicalDocs",
            text_key="text",
            embedding=embeddings,
        )
        
        # Perform similarity search
        docs = store.similarity_search(query, k=k, alpha=alpha)
        
        if not docs:
            return "No relevant medical documents found."
        
        # Format results
        result = f"Found {len(docs)} relevant medical document(s):\n\n"
        for i, doc in enumerate(docs, 1):
            result += f"**Result {i}:**\n{doc.page_content}\n\n"
            if doc.metadata:
                result += f"Source: {doc.metadata}\n\n"
        
        return result
        
    finally:
        weaviate_client.close()