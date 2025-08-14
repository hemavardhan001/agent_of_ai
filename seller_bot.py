import re

class SellerAgent:
    def __init__(self, name, personality_type, cost_price):
        self.name = name
        self.personality_type = personality_type
        self.cost_price = cost_price
        self.round = 0
        self.latest_buyer_offer = None
        self.last_offer = None
        # Set target price to achieve ~30% profit
        self.target_price = self.cost_price * 1.3  

    def observe_buyer(self, message: str):
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_buyer_offer = float(matches[0])

    def decide(self, market_price):
        """
        Optional market_price arg to unify CLI/Streamlit calls.
        """
        self.round += 1

        # Personality-based concession rates
        if self.personality_type == "Aggressive ":
            concession_rate = 0.20
        elif self.personality_type == "Diplomatic Seller":
            concession_rate = 0.10
        elif self.personality_type == "Data-Driven Seller":
            concession_rate = 0.15
        else:
            concession_rate = 0.12

        # Minimum acceptable price: 30% profit
        seller_low = self.cost_price * 1.3
        seller_high = self.cost_price * 1.4

        # Initial offer
        if self.round == 1:
            offer = (seller_low + seller_high) / 2
        else:
            prev = self.last_offer if self.last_offer else seller_low
            step = (seller_low - prev) * concession_rate
            offer = prev + step

        # Ensure we don’t go below the minimum target
        offer = max(offer, seller_low)

        # Accept if buyer offer meets target
        if self.latest_buyer_offer and seller_low <= self.latest_buyer_offer <= seller_high:
            return {"action": "accept", "offer": self.latest_buyer_offer,
                    "message": f"I accept your offer of ₹{self.latest_buyer_offer:.2f}."}

        # Walk away after too many rounds
        if self.round >= 10:
            return {"action": "walk_away", "offer": None, "message": "I cannot go lower. Goodbye."}

        self.last_offer = offer
        return {"action": "counter", "offer": offer, "message": f"My offer is ₹{offer:.2f}."}
