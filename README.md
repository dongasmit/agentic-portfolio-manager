# Agentic Portfolio Manager & Compliance AI 📈🤖

A full-stack WealthTech platform that combines live quantitative financial tracking with an Agentic AI assistant. Built to track multi-asset portfolios, calculate advanced performance metrics, and autonomously analyze holdings against strict firm compliance rules using a RAG (Retrieval-Augmented Generation) pipeline.

**[Live Demo](https://agentic-portfolio-manager.vercel.app/)** | **[Backend API Docs](https://your-backend-url.onrender.com/docs)**

## 🚀 Key Features
* **Quantitative Engine:** Calculates complex financial metrics including XIRR (Extended Internal Rate of Return), CAGR, and absolute returns using the Newton-Raphson method in Python.
* **Live Market Integration:** Built to connect seamlessly with the Zerodha Kite Connect API for real-time asset pricing and portfolio data.
* **Agentic AI Compliance:** Utilizes Google's Gemini 2.5 Flash and a Pinecone Vector Database to create a RAG pipeline. The AI agent actively reads portfolio distributions, compares them against injected regulatory guidelines, and dictates exact rebalancing trades (e.g., "Sell ₹18,300 of RELIANCE").
* **Cloud-Native Architecture:** Fully decoupled architecture with a Next.js frontend, a FastAPI backend, and a serverless PostgreSQL ledger database.

## 🛠️ Tech Stack
* **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Recharts
* **Backend:** Python, FastAPI, SciPy, Pandas
* **Database Layer:** PostgreSQL (Neon Serverless DB)
* **AI & Vector Search:** Google Gemini SDK (`google-genai`), Pinecone Vector DB
* **Deployment:** Vercel (Frontend), Render (Backend)

## 🏗️ Local Setup
To run this project locally, you will need two terminal instances.

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install -r requirements.txt
Create a .env file in the backend directory with your API keys (Database URL, Gemini, Pinecone, Kite Connect). Then run:

Bash
uvicorn main:app --reload
2. Frontend Setup
Bash
cd frontend
npm install
npm run dev
Open http://localhost:3000 to view the dashboard.
