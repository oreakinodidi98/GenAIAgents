import os
import re
from openai import AzureOpenAI
#from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
# for counting tokens in a text
import tiktoken
# for chunking large files into smaller pieces
import json
import uuid
from pathlib import Path
from typing import List
from azure.core.exceptions import ResourceNotFoundError
import hashlib

# For azure search
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    SearchField,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticSearch,
    SemanticField
)
# Load environment variables from .env file
load_dotenv()

INPUT_DIRECTORY = Path("./files/azure-ai-docs")
OUTPUT_DIRECTORY = Path("./files/chunks")

# Function to check for required environment variables
def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value.strip()

# Function to count the number of tokens in a string using tiktoken
def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name="cl100k_base")
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    #num_tokens = len(encoding.encode(text, disallowed_special=()))
    return num_tokens

# Function to clean markdown content by removing links, images, bold markers, and newlines
def clean_markdown_content(content: str) -> str:
    # Remove markdown links: [text](url) -> text
    link_pattern = r'\[([^\[]+)\]\(([^\)]+)\)'
    content = re.sub(link_pattern, r'\1', content)
    # Remove markdown images
    image_pattern = r'\!\[([^\[]*)\]\(([^\)]+)\)'
    content = re.sub(image_pattern, '', content)
    # Remove all occurrences of **, bold markers/newlines
    content = content.replace('**', '')
    content = content.replace('\n', '')
    return content


# Function to get embeddings vector for a given text using OpenAI embeddings model
def get_embeddings_vector(openai_client: AzureOpenAI, model_name: str, text: str) -> List[float]:
    response = openai_client.embeddings.create(
        input=text,
        model=model_name,
    )
    embedding = response.data[0].embedding
    return embedding

# Function to extract a specific frontmatter field from markdown content
def extract_frontmatter_field(content: str, field_name: str) -> str:
    # Supports: field: value
    match = re.search(rf"^{re.escape(field_name)}:\s*(.*)$", content, flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"')

# Function to retrieve context from the search index based on a question using semantic search
def retrieve_context(search_client: SearchClient, question: str, top: int = 5) -> str:
    results = search_client.search(
        search_text=question,
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="my-semantic-config",
        top=top,
        select=["page_title", "chunk_title", "chunk_content"],
    )
    chunks = []
    for r in results:
        chunks.append(
            f"[{r.get('page_title', '')} | {r.get('chunk_title', '')}]\n{r.get('chunk_content', '')}"
        )
    return "\n\n".join(chunks)

# Function to chunk markdown files into smaller sections and generate embeddings for each chunk
def chunk_markdown_files(
    openai_client: AzureOpenAI,
    embedding_model: str,
    embedding_vector_dimensions: int,
) -> List[Path]:
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    chunk_files: List[Path] = []

    if not INPUT_DIRECTORY.exists():
        raise FileNotFoundError(f"Input directory not found: {INPUT_DIRECTORY.resolve()}")
    # Initialize the chunk index counter
    chunk_index=0
    # Loop through each file in the directory
    for md_file in INPUT_DIRECTORY.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Minimal quality gates for docs
        if "## " not in content:
            print(f"Skipping {md_file.name}: no '##' sections found.")
            continue

        page_title = extract_frontmatter_field(content, "title") or md_file.stem
        page_description = extract_frontmatter_field(content, "description")
        page_date = extract_frontmatter_field(content, "ms.date")

        # Split on H2 sections
        sections = content.split("\n## ")[1:]  # Skip content before first H2
        if not sections:
            print(f"Skipping {md_file.name}: no section chunks produced.")
            continue

        for section in sections:
            section = section.strip()
            if not section:
                continue

            chunk_title = section.split("\n", 1)[0].strip()
            chunk_content = clean_markdown_content(section)

            token_count = num_tokens_from_string(chunk_content)
            if token_count > 8191:
                print(f"Skipping oversized chunk in {md_file.name} ({token_count} tokens).")
                continue

            vector = get_embeddings_vector(openai_client, embedding_model, chunk_content)
            if len(vector) != embedding_vector_dimensions:
                raise ValueError(
                    f"Embedding dimension mismatch for {md_file.name}. "
                    f"Expected {embedding_vector_dimensions}, got {len(vector)}"
                )

            stable_key = f"{md_file.name}|{chunk_title}".encode("utf-8")
            doc_id = hashlib.sha1(stable_key).hexdigest()

            chunk_doc = {
                #"id": str(uuid.uuid4()),
                "id": doc_id,
                "page_title": page_title,
                "page_description": page_description,
                "page_date": page_date,
                "chunk_title": chunk_title,
                "chunk_content": chunk_content,
                "vector": vector,
            }

            chunk_index += 1
            safe_title = re.sub(r'[\\/:*?"<>|]+', "", page_title).strip() or "untitled"
            chunk_path = OUTPUT_DIRECTORY / f"chunk_{chunk_index}_{safe_title}.json"
            chunk_path.write_text(json.dumps(chunk_doc, ensure_ascii=False, indent=2), encoding="utf-8")
            chunk_files.append(chunk_path)

    print(f"Created {len(chunk_files)} chunk file(s) in {OUTPUT_DIRECTORY.resolve()}")
    return chunk_files


def main():
    # Validate required environment variables
    azure_openai_endpoint = required_env("AZURE_OPENAI_ENDPOINT")
    chat_deployment = required_env("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")
    embedding_model = required_env("AZURE_OPENAI_EMBEDDING_MODEL")
    embedding_vector_dimensions = int(required_env("EMBEDDING_VECTOR_DIMENSIONS"))

    azure_search_service_endpoint = required_env("AZURE_SEARCH_SERVICE_ENDPOINT")
    azure_search_service_admin_key = required_env("AZURE_SEARCH_SERVICE_ADMIN_KEY")
    search_index_name = required_env("SEARCH_INDEX_NAME")

    print("ENDPOINT:", repr(azure_openai_endpoint))
    print("DEPLOYMENT:", repr(chat_deployment))
    print("INDEX:", repr(search_index_name))

    # Get Azure OpenAI and Azure Search configuration from environment variables
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), 
        "https://cognitiveservices.azure.com/.default"
    )

    # Initialize OpenAI client with Azure OpenAI endpoint and token provider
    openai_client = AzureOpenAI(
            azure_endpoint=azure_openai_endpoint, # https://<resource>.openai.azure.com
            azure_ad_token_provider=token_provider,
            api_version="2024-06-01",
        )

    # initialize Azure Search client
    credential = AzureKeyCredential(azure_search_service_admin_key)

    # Create Azure Search index client with the specified endpoint, index name, and credentials
    search_index_client = SearchIndexClient(
        endpoint=azure_search_service_endpoint, 
        #index_name=search_index_name, 
        credential=credential
    )

    # Create Azure Search client for performing search operations
    search_client = SearchClient(
        endpoint=azure_search_service_endpoint, 
        index_name=search_index_name, 
        credential=credential
    )

    # create or update search index
    fields = [
        SimpleField(name="id",type=SearchFieldDataType.String,key=True,sortable=True,filterable=True,facetable=True,),
        SearchableField(name="page_title", type=SearchFieldDataType.String),
        SearchableField(name="page_description", type=SearchFieldDataType.String),
        SearchableField(name="page_date", type=SearchFieldDataType.String),
        SearchableField(name="chunk_title", type=SearchFieldDataType.String),
        SearchableField(name="chunk_content", type=SearchFieldDataType.String),
        SearchField(
            name="vector", 
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=embedding_vector_dimensions, #1536,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myHnswProfile",algorithm_configuration_name="myHnsw")],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="page_title"),
            content_fields=[SemanticField(field_name="chunk_content")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])
    # Create the search index with the semantic settings
    search_index = SearchIndex(
        name=search_index_name, 
        fields=fields,
        vector_search=vector_search, 
        semantic_search=semantic_search,
    )

    # result = search_index_client.create_or_update_index(search_index)
    # print(f' {result.name} created')

    try:
        search_index_client.get_index(search_index_name)
        print(f"Index exists: {search_index_name}")
    except ResourceNotFoundError:
        result = search_index_client.create_index(search_index)
        print(f"Index created: {result.name}")

    # Chunk + embed files
    chunk_files = chunk_markdown_files(
        openai_client=openai_client,
        embedding_model=embedding_model,
        embedding_vector_dimensions=embedding_vector_dimensions,
    )

    if not chunk_files:
        raise RuntimeError("No chunk files were generated. Nothing to upload.")

    # Upload docs
    uploaded = 0
    for chunk_path in chunk_files:
        document = json.loads(chunk_path.read_text(encoding="utf-8"))
        upload_result = search_client.upload_documents(documents=[document])
        success = bool(upload_result and upload_result[0].succeeded)
        print(f"Upload {chunk_path.name}: {success}")
        if success:
            uploaded += 1

    print(f"Uploaded {uploaded}/{len(chunk_files)} document(s).")

    # Test connection to OpenAI ChatGPT

    question = "How to implement LLM in Python?"
    context = retrieve_context(search_client, question, top=5)

    completion = openai_client.chat.completions.create(
        model=chat_deployment,
        messages=[
            {"role": "system", "content": "You answer only from provided context. If context is missing, say you don't know."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    # completion = openai_client.chat.completions.create(
    #     model=chat_deployment,
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": "Who are you?"},
    #     ],
    #     extra_body={
    #         "data_sources": [
    #             {
    #                 "type": "azure_search",
    #                 "parameters": {
    #                     "endpoint": azure_search_service_endpoint,
    #                     "index_name": search_index_name,
    #                     "authentication": {
    #                         "type": "api_key",
    #                         "key": azure_search_service_admin_key,
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    # )
    
    print(completion.to_json())
    print("\nanswer:", completion.choices[0].message.content)

if __name__ == "__main__":
    main()