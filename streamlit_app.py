import streamlit as st
import time
import random
import re
from buyer_bot import BuyerAgent  # Keep your BuyerAgent file
# SellerAgent merged directly from your file
class SellerAgent:
    def __init__(self, name, personality_type, cost_price):
        self.name = name
        self.personality_type = personality_type
        self.cost_price = cost_price
        self.round = 0
        self.latest_buyer_offer = None
        self.last_offer = None

    def observe_buyer(self, message: str):
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_buyer_offer = float(matches[0])

    def decide(self):
        self.round += 1

        if self.personality_type == "Aggressive Trader":
            start_range = (1.35, 1.40)
            concession_rate = 0.20
        elif self.personality_type == "Diplomatic Seller":
            start_range = (1.30, 1.35)
            concession_rate = 0.10
        elif self.personality_type == "Data-Driven Seller":
            start_range = (1.32, 1.38)
            concession_rate = 0.15
        else:
            start_range = (1.30, 1.35)
            concession_rate = 0.12

        seller_low = self.cost_price * 1.30
        seller_high = self.cost_price * 1.40

        if self.round == 1:
            offer = self.cost_price * ((start_range[0] + start_range[1]) / 2)
        else:
            prev = self.last_offer if self.last_offer else self.cost_price * start_range[0]
            target = seller_low
            step = (target - prev) * concession_rate
            offer = prev + step

        if self.round >= 10:
            offer = seller_low

        offer = max(offer, seller_low)

        if self.latest_buyer_offer and seller_low <= self.latest_buyer_offer <= seller_high:
            return {"action": "accept", "offer": self.latest_buyer_offer,
                    "message": f"I accept your offer of ₹{self.latest_buyer_offer:.2f}."}

        self.last_offer = offer
        return {"action": "counter", "offer": offer,
                "message": f"My offer is ₹{offer:.2f}."}


# =========================
# Buyer/Seller Personas
# =========================
BUYER_PERSONAS = {
    "Aggressive Trader": {
        "openers": ["Alright, listen. What’s your rock-bottom price for {product}?"],
        "counter": ["Too high. How about ₹{}?"],
        "accepts": ["Fine. Done."],
        "walks": ["Forget it, I’m out."]
    },
    "Diplomatic Buyer": {
        "openers": ["Hi! I’m interested in {product}, let’s find a fair price."],
        "counter": ["Would you consider ₹{}?"],
        "accepts": ["Deal!"],
        "walks": ["Maybe another time."]
    }
}

# =========================
# Typing Effect
# =========================
def type_message(message, delay=0.02):
    placeholder = st.empty()
    text = ""
    for char in message:
        text += char
        placeholder.markdown(text)
        time.sleep(delay)
    return placeholder

# =========================
# Turn Handlers
# =========================
def buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message):
    buyer.observe_seller(seller_message)
    decision = buyer.decide(market_price)
    persona = BUYER_PERSONAS[buyer_personality]

    if round_num == 1:
        message = random.choice(persona["openers"]).format(product=product, market_price=market_price)
    elif decision['action'] == "accept":
        message = random.choice(persona["accepts"])
    elif decision['action'] == "walk_away":
        message = random.choice(persona["walks"])
    else:
        message = random.choice(persona["counter"]).format(decision['offer'])
    return decision, message

def seller_turn(seller, buyer_message):
    seller.observe_buyer(buyer_message)
    decision = seller.decide()
    return decision, decision['message']

# =========================
# Negotiation in Streamlit
# =========================
def run_negotiation_streamlit(product, market_price, buyer_name, buyer_personality, buyer_budget,
                              seller_name, seller_personality, seller_min_price,
                              typing_delay=0.02, round_pause=1):

    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    st.session_state.history = []
    seller_message = ""

    for round_num in range(1, 11):
        st.markdown(f"### Round {round_num}")
        time.sleep(round_pause)

        # BUYER TURN
        buyer_decision, buyer_message = buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message)
        type_message(f"**{buyer_name} ({buyer_personality})**: {buyer_message}", delay=typing_delay)
        if buyer_decision['action'] == "accept":
            st.success("✅ Deal closed successfully!")
            break

        # SELLER TURN
        time.sleep(round_pause)
        seller_decision, seller_message = seller_turn(seller, buyer_message)
        type_message(f"**{seller_name} ({seller_personality})**: {seller_message}", delay=typing_delay)
        if seller_decision['action'] == "accept":
            st.success("✅ Deal closed successfully!")
            break

        # Save history
        st.session_state.history.append({
            "round": round_num,
            "buyer_message": buyer_message,
            "seller_message": seller_message,
            "seller_action": seller_decision['action'],
            "seller_offer": seller_decision['offer']
        })

    # Show history
    if st.session_state.history:
        st.markdown("### Negotiation History")
        for turn in st.session_state.history:
            st.markdown(
                f"**Round {turn['round']}**  \n"
                f"Buyer: {turn['buyer_message']}  \n"
                f"Seller: {turn['seller_message']}  \n"
                f"Action: {turn['seller_action']} | Offer: ₹{turn['seller_offer']:.0f}"
            )

# =========================
# Streamlit UI
# =========================
st.title("🤝 Live Negotiation Simulator")

with st.form("negotiation_form"):
    product = st.text_input("Product Name","ENTER THE PRODUCT")
    market_price = st.number_input("Market Price (₹)")

    buyer_name = st.text_input("Buyer Name","ENTER")
    buyer_personality = st.selectbox("Buyer Personality", list(BUYER_PERSONAS.keys()))
    buyer_budget = st.number_input("Buyer Budget (₹)")

    seller_name = st.text_input("Seller Name","ENTER")
    seller_personality = st.selectbox("Seller Personality", ["Aggressive Trader", "Diplomatic Seller", "Data-Driven Seller", "Custom"])
    seller_min_price = st.number_input("Seller Minimum Price (₹)")

    submitted = st.form_submit_button("Start Negotiation")

if submitted:
    run_negotiation_streamlit(
        product, market_price,
        buyer_name, buyer_personality, buyer_budget,
        seller_name, seller_personality, seller_min_price
    )
