from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from services.quant_service import QuantService
from datetime import date
from services.ai_service import AIService
from pydantic import BaseModel
# Import our new service
from services.kite_service import KiteService

load_dotenv()

app = FastAPI(title="Agentic Portfolio Manager API")    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Allow frontend
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],
)

kite_service = KiteService()

def get_db_connection():
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.get("/")
def read_root():
    return {"status": "Engine is running", "service": "Portfolio Manager"}

@app.get("/api/health/db")
def check_db():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    cur.close()
    conn.close()
    return {"status": "success", "database_version": db_version['version']}

# --- KITE CONNECT ROUTES ---

@app.get("/api/kite/login")
def kite_login():
    """Redirects the user to the Zerodha login page."""
    login_url = kite_service.get_login_url()
    return RedirectResponse(url=login_url)

@app.get("/api/kite/callback")
@app.get("/api/kite/mock-callback")
def kite_callback(request_token: str):
    """Zerodha redirects back here with the request_token."""
    session_data = kite_service.generate_session(request_token)
    
    if not session_data:
        raise HTTPException(status_code=400, detail="Failed to generate Kite session")
        
    # In a real app, you would save this access_token in your database or a secure cookie
    return {
        "message": "Login successful!", 
        "access_token": session_data["access_token"]
    }

@app.get("/api/portfolio")
def get_portfolio():
    """Returns the current portfolio holdings."""
    holdings = kite_service.get_portfolio()
    return {"status": "success", "data": holdings}


   

@app.get("/api/metrics/returns/{client_id}")
def get_portfolio_returns(client_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Fetch all historical transactions
    cur.execute("SELECT * FROM transactions WHERE client_id = %s ORDER BY transaction_date ASC", (client_id,))
    transactions = cur.fetchall()
    cur.close()
    conn.close()

    if not transactions:
        return {"status": "error", "message": "No transactions found"}

    # 2. Prepare cash flows for XIRR
    cash_flows = [(t['transaction_date'], float(t['cash_flow'])) for t in transactions]
    
    # 3. Calculate CURRENT value of the portfolio
    # (In a real app, you loop through symbols and use kite.quote() here)
    # For now, we simulate current market prices: RELIANCE @ 2900, TCS @ 3900
    current_value = 0
    holdings_qty = {'RELIANCE': 0, 'TCS': 0}
    
    for t in transactions:
        if t['type'] == 'BUY':
            holdings_qty[t['symbol']] += float(t['quantity'])
        elif t['type'] == 'SELL':
            holdings_qty[t['symbol']] -= float(t['quantity'])
            
    current_value += holdings_qty['RELIANCE'] * 2900.0
    current_value += holdings_qty['TCS'] * 3900.0

    # XIRR requires the final current value to be added as a POSITIVE cash flow on today's date
    cash_flows.append((date.today(), current_value))

    # 4. Crunch the numbers
    xirr_rate = QuantService.calculate_xirr(cash_flows)
    
    total_invested = sum(abs(cf) for d, cf in cash_flows[:-1] if cf < 0)
    absolute_return = ((current_value - total_invested) / total_invested) * 100

    return {
        "status": "success",
        "metrics": {
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "absolute_return_percent": round(absolute_return, 2),
            "xirr_percent": round(xirr_rate * 100, 2)
        }
    }

# --- AI AGENT ROUTES ---

ai_service = AIService()

@app.get("/api/ai/seed")
def seed_db():
    """Populates the Vector DB with compliance rules."""
    return ai_service.seed_compliance_rules()

class ComplianceQuery(BaseModel):
    query: str

@app.post("/api/ai/analyze")
def analyze_compliance(query_data: ComplianceQuery):
    """Sends portfolio data to the AI Agent for analysis."""
    
    # 1. Get current holdings (We reuse the logic from /api/portfolio)
   # holdings_list = kite_service.get_portfolio()
    
    # 2. Calculate current value (Simplified logic for the agent)
    #current_value = 0
    #holdings_dict = {}
    
    #for item in holdings_list:
        #qty = float(item['quantity'])
        #price = float(item['last_price'])
        #current_value += qty * price
        #holdings_dict[item['tradingsymbol']] = {"qty": qty, "price": price}
        
# --- INJECT MOCK DATA FOR AI TESTING ---
    current_value = 63000.0
    holdings_dict = {
        "RELIANCE": {"qty": 15, "price": 2900}, # This equals ₹43,500 (69% of portfolio)
        "TCS": {"qty": 5, "price": 3900}        # This equals ₹19,500 (31% of portfolio)
    }
    # 3. Ask AI
    result = ai_service.analyze_portfolio(
        current_portfolio_value=current_value,
        holdings=holdings_dict,
        query=query_data.query
    )
    
    return {"status": "success", "ai_response": result}