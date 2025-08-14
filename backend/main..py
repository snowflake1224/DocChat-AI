import os
import uuid
from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.summarize import load_summarize_chain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import google.generativeai as genai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (for demo)
documents = {}

# Safety system message
SAFETY_PROMPT = """
You are a safety classifier. Analyze the user input and separate it into:
1. STORY: Personal context/narrative
2. QUERY: Actual information request

Evaluate ONLY the QUERY for:
- Nuclear weapons/radiation
- Illegal drug manufacturing
- Hate speech/terrorism
- Financial crimes
- Self-harm instructions

If the query violates safety policies, return: "UNSAFE: <reason>"
Otherwise return "SAFE"
"""

def extract_text(file_path: str, content_type: str) -> str:
    if content_type == "application/pdf":
        reader = PdfReader(file_path)
        return "".join(page.extract_text() for page in reader.pages)
    elif content_type == "text/plain":
        with open(file_path, 'r') as f:
            return f.read()
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    raise ValueError("Unsupported file type")

def summarize_text(text: str, api_key: str) -> str:
    # Initialize Google Gemini
    genai.configure(api_key=api_key)
    
    # Use Google's Gemini Pro model
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000)
    docs = text_splitter.create_documents([text])
    
    prompt_template = """Write a concise summary of the following document:
    {text}
    CONCISE SUMMARY:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    chain = load_summarize_chain(llm, chain_type="stuff", prompt=prompt)
    return chain.run(docs)

def is_safe_query(query: str, api_key: str) -> bool:
    # Initialize Google Gemini
    genai.configure(api_key=api_key)
    
    # Create safety model
    safety_model = genai.GenerativeModel('gemini-pro')
    
    # Generate safety response
    response = safety_model.generate_content(
        SAFETY_PROMPT + "\n\nUser Input: " + query,
        safety_settings={
            "HARM_CATEGORY_DANGEROUS": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
        }
    )
    
    # Check response
    if "SAFE" in response.text:
        return True
    return False

@app.post("/upload")
async def upload_file(file: UploadFile):
    # Validate file type
    valid_types = ["application/pdf", "text/plain", 
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if file.content_type not in valid_types:
        raise HTTPException(400, "Unsupported file type")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    
    try:
        # Extract text
        text = extract_text(temp_path, file.content_type)
    finally:
        os.unlink(temp_path)
    
    # Generate summary
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(500, "Google API key not configured")
    
    summary = summarize_text(text, api_key)
    
    # Store document
    doc_id = str(uuid.uuid4())
    documents[doc_id] = {
        "text": text,
        "filename": file.filename,
        "summary": summary
    }
    
    return {"doc_id": doc_id, "summary": summary}

@app.post("/chat")
async def chat_with_document(
    doc_id: str = Form(...),
    message: str = Form(...)
):
    if doc_id not in documents:
        raise HTTPException(404, "Document not found")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(500, "Google API key not configured")
    
    # Safety check
    if not is_safe_query(message, api_key):
        raise HTTPException(400, "Query violates safety policies")
    
    # Get document context
    context = documents[doc_id]["text"]
    
    # Generate response using Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # Create prompt with safety constraints
    prompt = f"""
    You are a helpful document assistant. Answer the user's question based ONLY on the provided document content.
    
    Document content:
    {context[:10000]}  # Limit context to 10k chars
    
    Question: {message}
    
    Important: If the question is not answerable from the document, say "I couldn't find that information in the document."
    """
    
    # Generate response
    response = model.generate_content(
        prompt,
        safety_settings={
            "HARM_CATEGORY_DANGEROUS": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
    )
    
    return {"response": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)