import streamlit as st
import re
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# -------------------- Buyer Agent --------------------
class BuyerAgent:
    def __init__(self, name, personality_type, resale_price):
        self.name = name
        self.personality_type = personality_type
        self.resale_price = resale_price
        self.round = 0
        self.latest_seller_offer = None
        self.last_offer = None
        self.market_price = None
        self.llm = ChatOllama(model="llama3.1:8b", temperature=0.6)

    def observe_seller(self, message: str):
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_seller_offer = float(matches[0])

    def decide(self, market_price: float):
        self.round += 1
        self.market_price = market_price

        # Personality ranges
        start_range, concession_rate = self._get_personality_params()

        # Profit range
        buyer_low = self.resale_price * 0.60
        buyer_high = self.resale_price * 0.70
        seller_low = market_price * 1.30
        seller_high = market_price * 1.40
        feasible_low = max(seller_low, buyer_low)
        feasible_high = min(seller_high, buyer_high)
        has_feasible = feasible_low <= feasible_high

        # Offer computation
        offer = self._compute_offer(start_range, concession_rate, feasible_low, feasible_high, seller_low, buyer_low)

        # ------------------- LLaMA message generation -------------------
        if self.latest_seller_offer and has_feasible and feasible_low <= self.latest_seller_offer <= feasible_high:
            prompt = f"""
            You are a Buyer AI negotiator with this personality: {self.personality_type}.
            Seller offered: ₹{self.latest_seller_offer}.
            You accept this offer. Respond naturally, politely, and concisely in 1–2 sentences.
            """
            message = self.llm.invoke(prompt).content
            return {"action": "accept", "offer": self.latest_seller_offer, "message": message}

        # Counter-offer
        self.last_offer = offer
        prompt = f"""
        You are a Buyer AI negotiator with this personality: {self.personality_type}.
        Seller offered: ₹{self.latest_seller_offer or 0}.
        You want to make a counteroffer of ₹{offer}. Respond naturally, politely, and concisely in 1–2 sentences.
        """
        message = self.llm.invoke(prompt).content
        return {"action": "counter", "offer": offer, "message": message}

    def _get_personality_params(self):
        if self.personality_type == "Aggressive Negotiator":
            return (0.50, 0.55), 0.20
        elif self.personality_type == "Diplomatic Buyer":
            return (0.58, 0.62), 0.10
        elif self.personality_type == "Data Analyst":
            return (0.56, 0.60), 0.15
        else:
            return (0.55, 0.60), 0.12

    def _compute_offer(self, start_range, concession_rate, feasible_low, feasible_high, seller_low, buyer_low):
        if self.round == 1:
            offer = self.resale_price * ((start_range[0] + start_range[1]) / 2)
        else:
            prev = self.last_offer if self.last_offer else self.resale_price * start_range[0]
            target = (feasible_low + feasible_high) / 2 if feasible_low <= feasible_high else (seller_low + buyer_low) / 2
            step = (target - prev) * concession_rate
            offer = prev + step
        if self.round >= 10:
            offer = feasible_low if feasible_low <= feasible_high else min(seller_low, buyer_low)
        return max(1.0, min(offer, self.resale_price))


# -------------------- Seller Agent --------------------
class SellerAgent:
    def __init__(self, name, personality_type, base_price):
        self.name = name
        self.personality_type = personality_type
        self.base_price = base_price
        self.round = 0
        self.latest_buyer_offer = None
        self.last_offer = None
        self.llm = ChatOllama(model="llama3.1:8b", temperature=0.6)

    def observe_buyer(self, message: str):
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_buyer_offer = float(matches[0])

    def decide(self):
        self.round += 1
        if self.latest_buyer_offer and self.latest_buyer_offer >= self.base_price:
            prompt = f"""
            You are a Seller AI negotiator with personality {self.personality_type}.
            Buyer offered ₹{self.latest_buyer_offer}.
            You accept this offer. Respond naturally, politely, in 1–2 sentences.
            """
            message = self.llm.invoke(prompt).content
            return {"action": "accept", "offer": self.latest_buyer_offer, "message": message}

        # Make counter-offer: slightly above last buyer offer or base_price
        counter_offer = max(self.latest_buyer_offer or 0, self.base_price) * 1.05
        prompt = f"""
        You are a Seller AI negotiator with personality {self.personality_type}.
        Buyer offered ₹{self.latest_buyer_offer or 0}.
        You want to make a counteroffer of ₹{counter_offer}. Respond naturally, politely, in 1–2 sentences.
        """
        message = self.llm.invoke(prompt).content
        self.last_offer = counter_offer
        return {"action": "counter", "offer": counter_offer, "message": message}


# -------------------- Streamlit UI --------------------
st.title("Buyer & Seller Negotiation Simulator")

if "buyer" not in st.session_state:
    st.session_state.buyer = None
if "seller" not in st.session_state:
    st.session_state.seller = None
if "history" not in st.session_state:
    st.session_state.history = []

with st.form(key='buyer_setup_form'):
    buyer_name = st.text_input("Buyer Name", "Alice")
    buyer_personality = st.selectbox("Buyer Personality", ["Aggressive Negotiator", "Diplomatic Buyer", "Data Analyst", "Custom"])
    resale_price = st.number_input("Buyer Future Resale Price (₹)", min_value=1000, max_value=10000000, value=50000)
with st.form(key='seller-setup-form'):
    seller_name = st.text_input("Seller Name", "Bob")
    seller_personality = st.selectbox("Seller Personality", ["Aggressive", "Friendly", "Analytical", "Custom"])
    base_price = st.number_input("Seller Base Price (₹)", min_value=1000, max_value=10000000, value=40000)

    setup_submitted = st.form_submit_button("Initialize Agents")

if setup_submitted:
    st.session_state.buyer = BuyerAgent(buyer_name, buyer_personality, resale_price)
    st.session_state.seller = SellerAgent(seller_name, seller_personality, base_price)
    st.session_state.history = []
    st.success("Buyer & Seller Agents initialized!")


# -------------------- Negotiation Round --------------------
if st.session_state.buyer and st.session_state.seller:
    st.markdown("### Negotiation Round")
    buyer_input = st.text_input("Enter Buyer Message (optional):", key="buyer_msg")
    seller_input = st.text_input("Enter Seller Message (optional):", key="seller_msg")

    if st.button("Next Step"):
        # Observe each other
        if buyer_input.strip():
            st.session_state.seller.observe_buyer(buyer_input)
        if seller_input.strip():
            st.session_state.buyer.observe_seller(seller_input)

        # Buyer decides
        buyer_decision = st.session_state.buyer.decide(st.session_state.seller.base_price)
        st.session_state.seller.observe_buyer(buyer_decision["message"])

        # Seller decides
        seller_decision = st.session_state.seller.decide()
        st.session_state.buyer.observe_seller(seller_decision["message"])

        # Record history
        st.session_state.history.append({
            "round": max(st.session_state.buyer.round, st.session_state.seller.round),
            "buyer_message": buyer_decision["message"],
            "buyer_offer": buyer_decision["offer"],
            "buyer_action": buyer_decision["action"],
            "seller_message": seller_decision["message"],
            "seller_offer": seller_decision["offer"],
            "seller_action": seller_decision["action"]
        })

    # Display history
    if st.session_state.history:
        st.markdown("### Negotiation History")
        for turn in st.session_state.history:
            st.markdown(
                f"**Round {turn['round']}**  \n"
                f"Buyer ({st.session_state.buyer.personality_type}): {turn['buyer_message']} | Offer: ₹{turn['buyer_offer']:.2f} | Action: {turn['buyer_action']}  \n"
                f"Seller ({st.session_state.seller.personality_type}): {turn['seller_message']} | Offer: ₹{turn['seller_offer']:.2f} | Action: {turn['seller_action']}"
            )
