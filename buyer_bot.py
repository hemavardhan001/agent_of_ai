import streamlit as st
import re
import time
from langchain_community.chat_models import ChatOllama

# -------------------- Buyer Agent --------------------
class BuyerAgent:
    def __init__(self, name, personality_type, budget):
        self.name = name
        self.personality_type = personality_type
        self.budget = budget
        self.round = 0
        self.latest_seller_offer = None
        self.last_offer = None
        self.llm = ChatOllama(model="llama3.1:8b", temperature=0.6)

    def observe_seller(self, message: str):
        """Extract numeric offer from seller’s message if present"""
        matches = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        if matches:
            self.latest_seller_offer = float(matches[0])

    def decide(self, market_price=None, max_rounds=6):
        """
        Decide buyer action based on seller offer.
        Ensures deal always closes by final round.
        """
        offer_to_consider = self.latest_seller_offer or market_price

        # --- If within budget early ---
        if offer_to_consider and offer_to_consider <= self.budget:
            prompt = f"""
            You are a {self.personality_type} buyer.
            Seller offered ₹{offer_to_consider}.
            Since this is within budget, agree politely in 1-2 short lines.
            """
            message = self.llm.invoke(prompt).content
            self.round += 1
            return {"action": "accept", "offer": offer_to_consider, "message": message}

        # --- If last round → force accept ---
        if self.round + 1 >= max_rounds:
            final_offer = offer_to_consider or self.budget
            prompt = f"""
            You are a {self.personality_type} buyer.
            It’s the final round. Politely accept ₹{final_offer} in 1-2 short lines.
            """
            message = self.llm.invoke(prompt).content
            self.round += 1
            return {"action": "accept", "offer": final_offer, "message": message}

        # --- Otherwise, progressive counter-offer ---
        if offer_to_consider:
            concession_factor = 0.9 + (0.02 * self.round)  # buyer concedes more each round
            counter_offer = min(offer_to_consider * concession_factor, self.budget)
        else:
            counter_offer = self.budget * (0.7 + 0.05 * self.round)

        prompt = f"""
        You are a {self.personality_type} buyer.
        Seller offered ₹{offer_to_consider or 0}.
        Make a short counter-offer around ₹{counter_offer:.2f}.
        Respond in 1–2 simple lines only.
        """
        message = self.llm.invoke(prompt).content
        self.last_offer = counter_offer
        self.round += 1
        return {"action": "counter", "offer": counter_offer, "message": message}


# -------------------- Typing Effect --------------------
def typing_effect(text, delay=0.03):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(delay)


# -------------------- Streamlit UI --------------------
st.title("🤝 Buyer Negotiation Simulator")

if "buyer" not in st.session_state:
    st.session_state.buyer = None
if "history" not in st.session_state:
    st.session_state.history = []
if "deal_reached" not in st.session_state:
    st.session_state.deal_reached = False

# Setup buyer
with st.form(key="buyer_setup_form"):
    buyer_name = st.text_input("Buyer Name", "Alice")
    buyer_personality = st.selectbox("Buyer Personality", ["Aggressive", "Friendly", "Analytical"])
    budget = st.number_input("Buyer Budget (₹)", min_value=1000, max_value=10000000, value=15000)

    setup_submitted = st.form_submit_button("Initialize Buyer Agent")

if setup_submitted:
    st.session_state.buyer = BuyerAgent(buyer_name, buyer_personality, budget)
    st.session_state.history = []
    st.session_state.deal_reached = False
    st.success("✅ Buyer Agent initialized!")

# Negotiation rounds
if st.session_state.buyer and not st.session_state.deal_reached:
    st.markdown(f"### Round {st.session_state.buyer.round + 1}")
    seller_input = st.text_input("✍️ Enter Seller Message / Offer:", key=f"seller_msg_{st.session_state.buyer.round}")

    if st.button("Next Step", disabled=not seller_input.strip()):
        st.session_state.buyer.observe_seller(seller_input)
        buyer_decision = st.session_state.buyer.decide()

        # Save turn
        st.session_state.history.append({
            "round": st.session_state.buyer.round,
            "seller_message": seller_input,
            "buyer_message": buyer_decision["message"],
            "buyer_offer": buyer_decision["offer"],
            "buyer_action": buyer_decision["action"]
        })

        if buyer_decision["action"] == "accept":
            st.session_state.deal_reached = True

# Show negotiation history
if st.session_state.history:
    st.markdown("### 📜 Negotiation History")
    for turn in st.session_state.history:
        st.markdown(
            f"**Round {turn['round']}**  \n"
            f"🏷️ Seller: {turn['seller_message']}  \n"
            f"👤 Buyer ({st.session_state.buyer.personality_type}):"
        )
        typing_effect(turn['buyer_message'])
        st.markdown(
            f"💰 Offer: ₹{turn['buyer_offer']:.0f} | Action: {turn['buyer_action']}"
        )

# Show final result
if st.session_state.deal_reached:
    final_price = st.session_state.history[-1]["buyer_offer"]
    st.success(f"🎉 Deal Reached! Final Agreed Price: ₹{final_price:.0f}")
