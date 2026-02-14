# SmartDoc AI - Intelligent Document Analyzer

SmartDoc AI is a premium, full-stack application that transforms static documents into interactive insights. Built with **Angular 16** and **FastAPI**, it leverages high-performance **Native Python Parsers** and cutting-edge **AI** (via Groq/Gemini/OpenAI) to perform real-time summarization, executive takeaways, and source-attributed Question & Answering.

![Angular](https://img.shields.io/badge/Angular-16.2-dd0031?style=flat&logo=angular)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat&logo=python)
![AI](https://img.shields.io/badge/AI-Groq_Gemini_OpenAI-f55036?style=flat)

## 🚀 Key Features

- **📄 Universal Document Parsing**:
  - Native support for **PDF**, **DOCX**, **RTF**, and **Excel** files.
  - No external dependencies like Java or Tika required for text extraction.
- **🧠 Advanced AI Capabilities**:
  - **Instant Summarization**: Choose between Executive, Detailed, or Simplified tones.
  - **Source Attribution**: AI automatically cites the source document `[Source: filename.ext]` for every claim.
  - **Executive Takeaways**: Automatically extracts 5 critical, high-level highlights from your documents.
  - **Context-Aware Q&A**: Ask complex questions about your documents and get precise, evidence-based answers.
- **✨ Premium UX/UI**:
  - Modern "Glassmorphism" design with Angular Material.
  - **Stateless & Private**: No data is stored in a database. Your documents stay in-memory for the duration of the analysis.
  - One-click export to **PDF** or **TXT**.

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- **Python 3.12+**
- **Node.js 16+** & **NPM**

### 2. Backend Setup (BYOK - Bring Your Own Key)
The backend runs on port **8081**. This project follows a **BYOK** model; you must provide your own API key for the AI provider (Groq, Gemini, or OpenAI).

**Install Dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

**Configure Environment:**
Create a `.env` file in the `backend/` directory:
```env
AI_PROVIDER_URL=https://api.groq.com/openai/v1/chat/completions
AI_PROVIDER_MODEL=llama-3.1-8b-instant
AI_PROVIDER_KEY=your_api_key_here
PORT=8081
```

**Run the Backend:**
```bash
python main.py
```

### 3. Frontend Setup
The frontend runs on port **4200**.

**Install & Run:**
```bash
cd frontend
npm install
npm start
```

---

## 🛡️ Security & Privacy Note
- **API Keys**: The `.env` file containing your private API keys is excluded from git via `.gitignore`. **NEVER commit your `.env` file.**
- **Stateless Execution**: This application does not use a database. Document text and analysis results exist strictly in-memory during the session and are cleared once the server/process is terminated.

---
*Developed with ❤️ using modern AI and Web Technologies - Feb 2026*
