import os
from kiteconnect import KiteConnect

class KiteService:
    def __init__(self):
        self.api_key = os.getenv("KITE_API_KEY", "mock_api_key")
        self.api_secret = os.getenv("KITE_API_SECRET", "mock_api_secret")
        self.kite = KiteConnect(api_key=self.api_key)
        
        # We will set this to True if you don't have real keys yet
        self.is_mock = self.api_key == "mock_api_key"

    def get_login_url(self):
        """Generates the URL to redirect the user to Zerodha's login page."""
        if self.is_mock:
            return "http://localhost:8000/api/kite/mock-callback?request_token=mock_token_123"
        return self.kite.login_url()

    def generate_session(self, request_token: str):
        """Exchanges the request token for an access token."""
        if self.is_mock:
            return {"access_token": "mock_access_token_456"}
            
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.kite.set_access_token(data["access_token"])
            return data
        except Exception as e:
            print(f"Error generating session: {e}")
            return None

    def get_portfolio(self):
        """Fetches the user's holdings (stocks currently owned)."""
        if self.is_mock:
            # Fake portfolio data for testing our XIRR engine later
            return [
                {"tradingsymbol": "RELIANCE", "quantity": 10, "average_price": 2500.0, "last_price": 2800.0},
                {"tradingsymbol": "TCS", "quantity": 5, "average_price": 3200.0, "last_price": 3150.0}
            ]
            
        try:
            return self.kite.holdings()
        except Exception as e:
            print(f"Error fetching portfolio: {e}")
            return []