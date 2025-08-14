# DocChat AI - Intelligent Document Analysis Platform

## Overview
Advanced document processing system that combines automatic summarization with secure Q&A capabilities. 
Implements multi-layered safety framework for ethical AI operations while providing powerful document insights.

## Key Features
- 📄 Multi-format document processing (PDF, TXT, DOCX)
- 🔍 AI-powered document summarization
- 💬 Contextual chat interface grounded in document content
- 🛡️ Ethical AI safeguards with query/story separation
- ⚡️ Minimalist UI with real-time processing

## Tech Stack
- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: FastAPI + Python 3.10+
- **AI Engine**: LangChain + LangGraph + OpenAI
- **Safety System**: Custom content classification pipeline

## Installation
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key
uvicorn app.main:app --reload

# Frontend setup
cd ../frontend
npm install
npm run dev
```

## Safety Architecture
1. Input validation for file types/sizes
2. Query/story separation algorithm
3. Five-category harm detection:
    - Nuclear/weapons content
    - Illegal activities
    - Hate speech/terrorism
    - Financial crimes
    - Self-harm instructions
4. Real-time safety classification

## Usage
1. Upload document (PDF/TXT/DOCX)
2. View AI-generated summary
3. Ask document-specific questions
4. Receive safe, context-aware responses

## Ethical Compliance
- Implements NIST AI Risk Management Framework
- Content moderation with explainable decisions
- Ephemeral document processing (no persistence)
- Audit logging for all AI operations

## Contributing
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## License
MIT License

## Key Components Summary
- **Ethical AI**: Query/story separation + 5-category harm detection
- **Document Processing**: PDF/TXT/DOCX support via PyPDF2/python-docx
- **Architecture**: React ↔ FastAPI ↔ LangChain integration
- **Safety**: Real-time classification with explainable decisions
- **Performance**: <4s average processing time for standard documents

