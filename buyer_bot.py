import streamlit as st
import re

# BuyerAgent class
class BuyerAgent:
    def __init__(self, name, personality_type, resale_price):
        self.name = name
        self.personality_type = personality_type
        self.resale_price = resale_price  # Manual input for profit calc
        self.round = 0
        self.latest_seller_offer = None
        self.last_offer = None
        self.market_price = None

    def observe_seller(self, message: str):
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_seller_offer = float(matches[0])

    def decide(self, market_price: float):
        self.round += 1
        self.market_price = market_price

        # Personality start ranges
        if self.personality_type == "Aggressive Negotiator":
            start_range = (0.50, 0.55)
            concession_rate = 0.20
        elif self.personality_type == "Diplomatic Buyer":
            start_range = (0.58, 0.62)
            concession_rate = 0.10
        elif self.personality_type == "Data Analyst":
            start_range = (0.56, 0.60)
            concession_rate = 0.15
        elif self.personality_type == "Custom":
            start_range = (0.55, 0.60)
            concession_rate = 0.12
        else:
            start_range = (0.55, 0.60)
            concession_rate = 0.12

        # Profit range for buyer (30–40% profit on resale price)
        buyer_low = self.resale_price * 0.60
        buyer_high = self.resale_price * 0.70

        # Seller's target range (for reference)
        seller_low = market_price * 1.30
        seller_high = market_price * 1.40

        feasible_low = max(seller_low, buyer_low)
        feasible_high = min(seller_high, buyer_high)
        has_feasible = feasible_low <= feasible_high

        # Offer computation
        if self.round == 1:
            offer = self.resale_price * ((start_range[0] + start_range[1]) / 2)
        else:
            prev = self.last_offer if self.last_offer else self.resale_price * start_range[0]
            if has_feasible:
                target = (feasible_low + feasible_high) / 2.0
            else:
                if seller_low > buyer_high:
                    target = (buyer_high + seller_low) / 2.0
                else:
                    target = (seller_high + buyer_low) / 2.0
            step = (target - prev) * concession_rate
            offer = prev + step

        if self.round >= 10:
            offer = feasible_low if has_feasible else min(seller_low, buyer_low)

        offer = max(1.0, min(offer, self.resale_price))

        # Auto-accept rules
        if self.latest_seller_offer:
            if has_feasible and feasible_low <= self.latest_seller_offer <= feasible_high:
                return {"action": "accept", "offer": self.latest_seller_offer,
                        "message": f"I accept your offer of ₹{self.latest_seller_offer:.2f}."}

        self.last_offer = offer
        return {"action": "counter", "offer": offer,
                "message": f"My offer is ₹{offer:.2f}."}


# -------------------- Streamlit UI --------------------
st.title("Buyer Agent Negotiation Simulator")

if "buyer" not in st.session_state:
    st.session_state.buyer = None
if "history" not in st.session_state:
    st.session_state.history = []

with st.form(key='setup_form'):
    buyer_name = st.text_input("Buyer Name", "Alice")
    buyer_personality = st.selectbox(
        "Buyer Personality",
        ["Aggressive Negotiator", "Diplomatic Buyer", "Data Analyst", "Custom"]
    )
    resale_price = st.number_input("Future Resale Price (₹)", min_value=1000, max_value=10000000, value=50000)
    market_price = st.number_input("Market Price (₹)", min_value=1000, max_value=10000000, value=42000)
    setup_submitted = st.form_submit_button("Initialize Buyer Agent")

if setup_submitted:
    st.session_state.buyer = BuyerAgent(buyer_name, buyer_personality, resale_price)
    st.session_state.history = []
    st.success("Buyer Agent initialized!")

if st.session_state.buyer:
    st.markdown("### Negotiation Round")
    seller_message = st.text_input("Enter Seller's offer message:", key="seller_msg")

    if st.button("Buyer Decide"):
        if not seller_message.strip():
            st.warning("Please enter the seller's offer message.")
        else:
            st.session_state.buyer.observe_seller(seller_message)
            decision = st.session_state.buyer.decide(market_price)

            seller_offer = st.session_state.buyer.latest_seller_offer
            seller_profit_pct = None
            buyer_profit_pct = None

            if seller_offer:
                seller_profit_pct = ((seller_offer - market_price) / market_price) * 100.0
            if decision["offer"] is not None and st.session_state.buyer.resale_price > 0:
                buyer_profit_pct = ((st.session_state.buyer.resale_price - decision["offer"]) /
                                    decision["offer"]) * 100.0

            st.session_state.history.append({
                "round": st.session_state.buyer.round,
                "seller_message": seller_message,
                "buyer_action": decision['action'],
                "buyer_offer": decision['offer'],
                "buyer_message": decision['message'],
                "seller_profit_percent": seller_profit_pct,
                "buyer_profit_percent": buyer_profit_pct
            })

    if st.session_state.history:
        st.markdown("### Negotiation History")
        for turn in st.session_state.history:
            sp = f"{turn['seller_profit_percent']:.2f}%" if turn['seller_profit_percent'] is not None else "—"
            bp = f"{turn['buyer_profit_percent']:.2f}%" if turn['buyer_profit_percent'] is not None else "—"
            st.markdown(
                f"**Round {turn['round']}**  \n"
                f"Seller: {turn['seller_message']}  \n"
                f"Buyer ({st.session_state.buyer.personality_type}): {turn['buyer_message']}  \n"
                f"Action: {turn['buyer_action']} | Offer: ₹{turn['buyer_offer']:.2f}  \n"
                f"Seller Profit vs Market: {sp} | Buyer Profit vs Offer: {bp}"
            )
