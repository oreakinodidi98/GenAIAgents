
from foundry_local import FoundryLocalManager
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

# ============================================================
# STEP 1: Initialize the Local AI Model
# ============================================================
alias = "qwen2.5-0.5b"  # Small, fast model for local use

# Connect to existing Foundry service
manager = FoundryLocalManager(alias)

# Configure ChatOpenAI to use the local model
# Think of this as creating a "phone line" to your local AI
llm = ChatOpenAI(
    model=manager.get_model_info(alias).id,  # Get the exact model ID
    base_url=manager.endpoint,               # Where the model is running (localhost)
    api_key=manager.api_key,                 # Not needed for local, but required by API
    temperature=0.7,                         # Creativity: 0=focused, 1=random
    streaming=False                          # Wait for complete response
)

def main():
    # ============================================================
    # STEP 2: Load the PDF Document
    # ============================================================
    pdf_path = Path("Policy Insurance Product Information Document.PDF")

    if not pdf_path.exists():
        print(f" PDF file not found at {pdf_path}")
        return

    print(f" PDF found at {pdf_path}")
    print("\nLoading PDF content...")
    
    # PyPDFLoader reads the PDF and splits it into pages
    # Each page becomes a separate "document" object
    loader = PyPDFLoader(pdf_path)
    all_pages = loader.load()
    
    # For this demo, use all pages (or limit if it's too large)
    # Example: documents = all_pages[:10] would only use first 10 pages
    documents = all_pages
    
    print(f"Successfully loaded PDF with {len(all_pages)} pages")
    total_chars = sum(len(doc.page_content) for doc in documents)
    print(f"Total characters: {total_chars:,}")
    
    # ============================================================
    # STEP 3: Create the Prompt Template
    # ============================================================
    # This defines HOW we want to talk to the AI
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",  # System message: Sets the AI's behavior/role
            "You are a helpful assistant that summarizes the document. "
            "Provide clear, concise summaries. Return only the summary, no extra text."
        ),
        (
            "human",   # User message: The actual request
            "{input}"  # {input} is a placeholder we'll fill in later
        )
    ])
    
    # ============================================================
    # STEP 4: Build the Chain (Prompt + Model)
    # ============================================================
    # The | operator connects prompt → model (Prompt -> LLM -> Answer)
    # When data flows through, it goes: your text → prompt → AI → response
    chain = prompt | llm
    
    # ============================================================
    # STEP 5: Process Document in Chunks
    # ============================================================
    # Why chunks? The model has a limit on how much text it can process at once
    # Chunking = divide the document into smaller pieces, summarize each piece
    
    chunk_size = 3  # Summarize 3 pages at a time (adjust based on your needs)
    summaries = []
    
    print(f"\nSummarizing document in chunks of {chunk_size} pages...")
    print(f"{'='*60}\n")
    
    # Loop through documents in chunks
    # range(0, len(documents), chunk_size) creates: 0, 3, 6, 9, ...
    for i in range(0, len(documents), chunk_size):
        # Get the current chunk (e.g., pages 0-2, then 3-5, then 6-8)
        chunk = documents[i:i+chunk_size]
        
        # Combine all pages in this chunk into one string
        # .page_content gets the actual text from each page
        chunk_content = "\n\n".join([doc.page_content for doc in chunk])
        
        # Calculate which pages we're processing
        start_page = i + 1
        end_page = min(i + chunk_size, len(documents))
        
        print(f"📖 Processing pages {start_page}-{end_page}...")
        
        # ============================================================
        # STEP 6: Invoke the Chain (Send to AI and Get Response)
        # ============================================================
        # invoke() executes the chain:
        # 1. Takes chunk_content and fills in the {input} placeholder
        # 2. Sends the complete prompt to the AI model
        # 3. Waits for the AI to generate a response
        # 4. Returns the response as ai_msg
        ai_msg = chain.invoke({
            "input": chunk_content
        })
        
        # ai_msg.content contains the actual summary text
        summaries.append(ai_msg.content)
        print(f"✅ Completed pages {start_page}-{end_page}\n")
    
    # ============================================================
    # STEP 7: Display All Summaries
    # ============================================================
    print(f"\n{'='*60}")
    print("📝 CHUNK SUMMARIES:")
    print(f"{'='*60}\n")
    
    for idx, summary in enumerate(summaries, 1):
        print(f"--- Chunk {idx} ---")
        print(summary)
        print()
    
    # ============================================================
    # OPTIONAL: Create a Final Combined Summary
    # ============================================================
    print(f"\n{'='*60}")
    print("📋 CREATING FINAL SUMMARY FROM ALL CHUNKS...")
    print(f"{'='*60}\n")
    
    # Combine all chunk summaries into one text
    combined_summaries = "\n\n".join(summaries)
    
    # Create a new prompt to summarize the summaries
    final_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful assistant. Create a cohesive final summary from these chunk summaries."
        ),
        (
            "human",
            "Here are summaries of different sections of an insurance document. "
            "Create one coherent final summary:\n\n{input}"
        )
    ])
    
    final_chain = final_prompt | llm
    final_response = final_chain.invoke({"input": combined_summaries})
    
    print(f"{'='*60}")
    print("🎯 FINAL SUMMARY:")
    print(f"{'='*60}")
    print(final_response.content)
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
