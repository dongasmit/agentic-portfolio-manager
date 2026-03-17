import os
from google import genai
from google.genai import types
from pinecone import Pinecone

class AIService:
    def __init__(self):
        # 1. Initialize the new Google GenAI Client
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # 2. Configure Pinecone
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if self.index_name in [idx.name for idx in self.pc.list_indexes()]:
            self.index = self.pc.Index(self.index_name)

    def get_embedding(self, text: str):
        """Generates a 768-dimensional vector using Google's new SDK."""
        response = self.gemini_client.models.embed_content(
            model="gemini-embedding-001", 
            contents=text,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        # The new SDK returns a list of embeddings. We grab the first one's values.
        return response.embeddings[0].values

    def seed_compliance_rules(self):
        rule = "Aggressive Risk Profile Rule: A single stock cannot exceed 40% of the total portfolio value. If it does, the advisor must sell the excess and rebalance."
        
        vector = self.get_embedding(rule)
        self.index.upsert(vectors=[{"id": "rule_1", "values": vector, "metadata": {"text": rule}}])
        return "Rules seeded successfully into Pinecone using the new SDK."

    def analyze_portfolio(self, current_portfolio_value: float, holdings: dict, query: str):
        # 1. Retrieve the rule from Pinecone
        query_vector = self.get_embedding(query)
        pinecone_res = self.index.query(vector=query_vector, top_k=1, include_metadata=True)
        
        rules = pinecone_res['matches'][0]['metadata']['text'] if pinecone_res['matches'] else "No rules found."

       # 2. Construct the Prompt (Updated for flexibility)
        prompt = f"""
        You are an expert WealthTech AI agent assisting a financial advisor.
        
        Firm Compliance Guidelines: {rules}
        Client Portfolio Value: ₹{current_portfolio_value}
        Current Holdings: {holdings}
        
        Advisor Query: {query}
        
        Instructions:
        1. Answer the Advisor's query directly and concisely.
        2. If the query asks about buying new shares or rebalancing, ALWAYS check the Current Holdings against the Firm Compliance Guidelines first.
        3. If the current portfolio is already in breach of a rule (e.g., a stock is over 40%), firmly warn the advisor and calculate exactly how much needs to be sold before they can buy anything else.
        4. If they ask for stock recommendations, remind them that as an AI, you suggest broad sectors (like Tech or Pharma) or ETFs for diversification, not individual stock picks.
        """

        # 3. Get the AI Decision using the latest Flash model
        response = self.gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text