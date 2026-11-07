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
# For azure search
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

# Get Azure OpenAI and Azure Search configuration from environment variables
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_chat_completions_deployment_name = os.getenv("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    "https://cognitiveservices.azure.com/.default"
)
azure_openai_embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
embedding_vector_dimensions = os.getenv("EMBEDDING_VECTOR_DIMENSIONS")
azure_search_service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
azure_search_service_admin_key = os.getenv("AZURE_SEARCH_SERVICE_ADMIN_KEY")
search_index_name = os.getenv("SEARCH_INDEX_NAME")

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
    index_name=search_index_name, 
    credential=credential
)

# Create Azure Search client for performing search operations
search_client = SearchClient(endpoint=azure_search_service_endpoint, index_name=search_index_name, credential=credential)

# Function to check for required environment variables
def required_env(name):
    value = os.getenv(name)
    if not value or not value.strip():
        raise ValueError(f"Missing environment variable: {name}")
    return value.strip()

# Function to count the number of tokens in a string using tiktoken
def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name="cl100k_base")
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    return num_tokens

# Function to clean markdown content by removing links, images, bold markers, and newlines
def clean_markdown_content(content):
    # Remove links
    link_pattern = r'\[([^\[]+)\]\(([^\)]+)\)'
    content = re.sub(link_pattern, r'\1', content)
    # Remove images
    image_pattern = r'\!\[([^\[]*)\]\(([^\)]+)\)'
    content = re.sub(image_pattern, '', content)
    # Remove all occurrences of **
    content = content.replace('**', '')
    content = content.replace('\n', '')
    return content

# Function to get embeddings vector for a given text using OpenAI embeddings model
def get_embeddings_vector(text):
    response = openai_client.embeddings.create(
        input=text,
        model=azure_openai_embedding_model,
    )
    embedding = response.data[0].embedding
    return embedding

def extract_frontmatter_field(content: str, field_name: str) -> str:
    # Supports: field: value
    match = re.search(rf"^{re.escape(field_name)}:\s*(.*)$", content, flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip('"')

def chunk_markdown_files(file_content, chunk_size=8191):
    input_directory = './files/azure-ai-docs/'
    output_directory = './files/chunks/'
    # create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    # Initialize the chunk index counter
    chunk_index=0
    # Loop through each file in the directory
    for filename in os.listdir(input_directory):
        # Check if the file is a markdown file
        if filename.endswith('.md'):
            # Open the file
            with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as file:
                print(filename)
                # Read the file content
                content = file.read()
                
                # break if content doesn't contain title, description, ms.date and '##'
                if 'title:' not in content or 'description:' not in content or 'ms.date:' not in content or '##' not in content:
                    print(f'File {filename} does not contain title, description, ms.date or ##')
                    continue

                # Extract the title, description, and date
                page_title = re.search(r'title: (.*)', content).group(1).replace('"', '')
                page_description = re.search(r'description: (.*)', content).group(1)
                page_date = re.search(r'ms.date: (.*)', content).group(1)
                
                # Split the content into chunks based on '##'
                chunks = content.split('\n## ')[1:]  # Skip the first chunk as it contains the title, description, and date
                
                # Add the chunks to the list along with the title, description, and date
                for chunk in chunks:
                    chunk_index=chunk_index + 1
                    chunk_content = clean_markdown_content(chunk.strip())
                    
                    if (num_tokens_from_string(chunk_content) > 8191):
                        print(f'Chunk {chunk_index} in file {filename} has more than 8191 tokens')
                        break

                    vector = get_embeddings_vector(chunk_content)
                    
                    chunk = {
                        "id": str(uuid.uuid4()),
                        'page_title': page_title,
                        'page_description': page_description,
                        'page_date': page_date,
                        'chunk_title': chunk.split('\n')[0],  # The first line after '##' is the title of the chunk
                        'chunk_content': chunk_content,  # Remove leading and trailing whitespaces
                        'vector': vector
                    }
                    # Save the chunk to a file in the output directory
                    output_filename = os.path.join(output_directory, f'{filename}_chunk_{chunk_index}.json')
                    with open(output_filename, 'w', encoding='utf-8') as output_file:
                        json.dump(chunk, output_file, ensure_ascii=False, indent=4)
                    
                    chunk_file_name = f'chunk_{chunk_index}_{page_title}.json'.replace('?', '').replace(':', '').replace("'", '').replace('|', '').replace('/', '').replace('\\', '')

                    # write chunk into JSON file into output directory
                    with open(f'{output_directory}/{chunk_file_name}', 'w') as f:
                        json.dump(chunk, f)


def main():
    # Validate required environment variables
    required_env("AZURE_OPENAI_ENDPOINT")
    required_env("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")
    required_env("AZURE_OPENAI_EMBEDDING_MODEL")
    required_env("EMBEDDING_VECTOR_DIMENSIONS")
    required_env("AZURE_SEARCH_SERVICE_ENDPOINT")
    required_env("AZURE_SEARCH_SERVICE_ADMIN_KEY")
    required_env("SEARCH_INDEX_NAME")

    print("ENDPOINT:", repr(os.getenv("AZURE_OPENAI_ENDPOINT")))
    print("DEPLOYMENT:", repr(os.getenv("AZURE_OPENAI_CHAT_COMPLETIONS_DEPLOYMENT_NAME")))

    # Setting input directory for markdown files
    input_directory = './files/azure-ai-docs/'
    i=0
    # Iterate through all markdown files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.md'):
            with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                tokens = num_tokens_from_string(content)
                if tokens > 8191:
                    print(f'File {filename} has {tokens} tokens which is more than 8191 (max) tokens')

    # openai_client = AzureOpenAI(
    #     azure_endpoint=azure_openai_endpoint, # https://<resource>.openai.azure.com
    #     azure_ad_token_provider=token_provider,
    #     api_version="2024-06-01",
    # )

    # create search index
    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            sortable=True,
            filterable=True,
            facetable=True,
        ),
        SearchableField(name="page_title", type=SearchFieldDataType.String),
        SearchableField(name="page_description", type=SearchFieldDataType.String),
        SearchableField(name="page_date", type=SearchFieldDataType.String),
        SearchableField(name="chunk_title", type=SearchFieldDataType.String),
        SearchableField(name="chunk_content", type=SearchFieldDataType.String),
        SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=3072, #1536,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    # Configure the vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="page_title"),
            # keywords_fields=[SemanticField(field_name="category")],
            content_fields=[SemanticField(field_name="chunk_content")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])
    # Create the search index with the semantic settings
    search_index = SearchIndex(name=search_index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = search_index_client.create_or_update_index(search_index)
    print(f' {result.name} created')

    for filename in os.listdir(output_directory):
        if filename.endswith('.json'):
            with open(os.path.join(output_directory, filename), 'r') as file:
                document = json.load(file)

                result = search_client.upload_documents(documents=document)
                print(f"Upload of {filename} succeeded: { result[0].succeeded }")

    # Test connection to OpenAI ChatGPT
    completion = openai_client.chat.completions.create(
        model=azure_openai_chat_completions_deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who are you?"},
        ],
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": azure_search_service_endpoint,
                        "index_name": search_index_name,
                        "authentication": {
                            "type": "api_key",
                            "key": azure_search_service_admin_key,
                        }
                    }
                }
            ]
        }
    )
    
    print(completion.to_json())
    print("\nanswer:", completion.choices[0].message.content)

if __name__ == "__main__":
    main()