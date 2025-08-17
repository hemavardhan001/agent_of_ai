import streamlit as st
import re
from langchain_community.chat_models import ChatOllama

# -------------------- Seller Agent --------------------
class SellerAgent:
    def __init__(self, name, personality_type, min_price=None, min_rounds=3):
        self.name = name
        self.personality_type = personality_type
        self.min_price = min_price if min_price else cost_price * 0.8  # fallback min price
        self.round = 0
        self.latest_buyer_offer = None
        self.last_offer = None
        self.min_rounds = min_rounds     # ✅ must negotiate at least X rounds
        self.deal_closed = False
        self.llm = ChatOllama(model="llama3.1:8b", temperature=0.6)

    def observe_buyer(self, message: str):
        """Extract numeric offer from buyer’s message if present"""
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_buyer_offer = float(matches[0])

    def decide(self):
        """
        Decide seller action based on buyer offer.
        Returns dict with action, offer, and message.
        """
        self.round += 1
        offer_to_consider = self.latest_buyer_offer

        # ✅ Force deal success only after min_rounds
        if self.round >= self.min_rounds:
            self.deal_closed = True
            final_offer = offer_to_consider or self.cost_price
            prompt = f"""
            You are a {self.personality_type} seller.
            After thoughtful negotiation, you’ve decided to close the deal at ₹{final_offer}.
            Respond with a short, positive acceptance in 1–2 lines.
            """
            message = self.llm.invoke(prompt).content
            return {"action": "accept", "offer": final_offer, "message": message}

        # Otherwise → keep negotiating (counter-offer)
        if offer_to_consider:
            counter_offer = max(offer_to_consider * 1.1, self.min_price)
        else:
            counter_offer = self.cost_price * 1.2  # start a bit higher than cost

        prompt = f"""
        You are a {self.personality_type} seller.
        Buyer offered ₹{offer_to_consider or 0}.
        Make a counter-offer around ₹{counter_offer:.2f}.
        Respond briefly in 1–2 lines.
        """
        message = self.llm.invoke(prompt).content
        self.last_offer = counter_offer
        return {"action": "counter", "offer": counter_offer, "message": message}


# -------------------- Streamlit UI --------------------
st.title("Seller Negotiation Simulator")

if "seller" not in st.session_state:
    st.session_state.seller = None
if "history" not in st.session_state:
    st.session_state.history = []
if "deal_reached" not in st.session_state:
    st.session_state.deal_reached = False

# Setup seller
with st.form(key="seller_setup_form"):
    seller_name = st.text_input("Seller Name", "Bob")
    seller_personality = st.selectbox("Seller Personality", ["Tough", "Friendly", "Data-Driven"])
    cost_price = st.number_input("Seller Cost Price (₹)", min_value=1000, max_value=10000000, value=12000)
    min_price = st.number_input("Seller Minimum Price (₹)", min_value=1000, max_value=10000000, value=10000)
    min_rounds = st.slider("Minimum Rounds Before Closure", min_value=1, max_value=10, value=3)

    setup_submitted = st.form_submit_button("Initialize Seller Agent")

if setup_submitted:
    st.session_state.seller = SellerAgent(seller_name, seller_personality, cost_price, min_price, min_rounds)
    st.session_state.history = []
    st.session_state.deal_reached = False
    st.success("✅ Seller Agent initialized!")

# Negotiation rounds
if st.session_state.seller and not st.session_state.deal_reached:
    st.markdown(f"### Negotiation Round {st.session_state.seller.round + 1}")
    buyer_input = st.text_input("Enter Buyer Message / Offer:", key=f"buyer_msg_{st.session_state.seller.round}")

    if st.button("Next Step", disabled=not buyer_input.strip()):
        st.session_state.seller.observe_buyer(buyer_input)
        seller_decision = st.session_state.seller.decide()

        # Save turn
        st.session_state.history.append({
            "round": st.session_state.seller.round,
            "buyer_message": buyer_input,
            "seller_message": seller_decision["message"],
            "seller_offer": seller_decision["offer"],
            "seller_action": seller_decision["action"]
        })

        if seller_decision["action"] == "accept":
            st.session_state.deal_reached = True

# Show negotiation history
if st.session_state.history:
    st.markdown("### Negotiation History")
    for turn in st.session_state.history:
        st.markdown(
            f"**Round {turn['round']}**  \n"
            f"👤 Buyer: {turn['buyer_message']}  \n"
            f"🏷️ Seller ({st.session_state.seller.personality_type}): {turn['seller_message']}  \n"
            f"💰 Offer: ₹{turn['seller_offer']:.0f} | Action: {turn['seller_action']}"
        )

# Show final result
if st.session_state.deal_reached:
    final_price = st.session_state.history[-1]["seller_offer"]
    st.success(f"✅ Deal Reached Successfully! Final Agreed Price: ₹{final_price:.0f}")
