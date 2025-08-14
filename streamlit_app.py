import streamlit as st
import time
import random
import re
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from buyer_bot import BuyerAgent  # Keep your BuyerAgent file

# -------------------------
# Seller Agent with LLaMA
# -------------------------
class SellerAgent:
    def __init__(self, name, personality_type, cost_price):
        self.name = name
        self.personality_type = personality_type
        self.cost_price = cost_price
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
        self.last_offer = offer

        # Auto-accept if buyer offer is acceptable
        if self.latest_buyer_offer and seller_low <= self.latest_buyer_offer <= seller_high:
            prompt = f"You are a {self.personality_type} Seller. Buyer offered ₹{self.latest_buyer_offer}. Accept politely in 1-2 sentences."
            chat_prompt = ChatPromptTemplate.from_template(prompt)
            formatted_messages = chat_prompt.format_messages()
            message = self.llm.invoke(formatted_messages).content
            return {"action": "accept", "offer": self.latest_buyer_offer, "message": message}

        # Otherwise generate counter-offer message
        prompt = f"You are a {self.personality_type} Seller. Buyer offered ₹{self.latest_buyer_offer or 0}. You counter with ₹{offer}. Respond naturally in 1-2 sentences."
        chat_prompt = ChatPromptTemplate.from_template(prompt)
        formatted_messages = chat_prompt.format_messages()
        message = self.llm.invoke(formatted_messages).content

        return {"action": "counter", "offer": offer, "message": message}


# -------------------------
# Typing Effect
# -------------------------
def type_message(message, delay=0.02):
    placeholder = st.empty()
    text = ""
    for char in message:
        text += char
        placeholder.markdown(text)
        time.sleep(delay)
    return placeholder


# -------------------------
# Turn Handlers
# -------------------------
def buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message):
    buyer.observe_seller(seller_message)
    decision = buyer.decide(market_price)

    if decision['action'] == "accept":
        prompt = f"You are a {buyer_personality} Buyer. Accept seller's offer of ₹{buyer.latest_seller_offer}. Respond politely."
    elif decision['action'] == "walk_away":
        prompt = f"You are a {buyer_personality} Buyer. You decide to walk away from the deal. Respond politely."
    else:
        prompt = f"You are a {buyer_personality} Buyer. Seller offered ₹{buyer.latest_seller_offer or 0}. Counter with ₹{decision['offer']} naturally."

    chat_prompt = ChatPromptTemplate.from_template(prompt)
    formatted_messages = chat_prompt.format_messages()
    message = buyer.llm.invoke(formatted_messages).content

    return decision, message


def seller_turn(seller, buyer_message):
    seller.observe_buyer(buyer_message)
    decision = seller.decide()
    return decision, decision['message']


# -------------------------
# Main Negotiation Loop
# -------------------------
def run_negotiation_streamlit(product, market_price, buyer_name, buyer_personality, buyer_budget,
                              seller_name, seller_personality, seller_min_price,
                              typing_delay=0.02, round_pause=1):

    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    buyer.llm = ChatOllama(model="llama3.1:8b", temperature=0.6)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    st.session_state.history = []
    seller_message = ""

    for round_num in range(1, 11):
        st.markdown(f"### Round {round_num}")
        time.sleep(round_pause)

        # Buyer Turn
        buyer_decision, buyer_message = buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message)
        type_message(f"**{buyer_name} ({buyer_personality})**: {buyer_message}", delay=typing_delay)
        if buyer_decision['action'] == "accept":
            st.success("✅ Deal closed successfully!")
            break

        # Seller Turn
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


# -------------------------
# Streamlit UI
# -------------------------
st.title("🤝 AI Negotiation Simulator with LLaMA 3.1:8b")

with st.form("negotiation_form"):
    product = st.text_input("Product Name", "ENTER THE PRODUCT")
    market_price = st.number_input("Market Price (₹)", min_value=1000, max_value=100000, value=15000)

    buyer_name = st.text_input("Buyer Name", "ENTER")
    buyer_personality = st.selectbox("Buyer Personality", ["Aggressive Trader", "Diplomatic Buyer", "Data-Driven Analyst", "Creative Wildcard"])
    buyer_budget = st.number_input("Buyer Budget (₹)", min_value=1000, max_value=100000, value=16000)

    seller_name = st.text_input("Seller Name", "ENTER")
    seller_personality = st.selectbox("Seller Personality", ["Aggressive Trader", "Diplomatic Seller", "Data-Driven Seller", "Creative Wildcard"])
    seller_min_price = st.number_input("Seller Minimum Price (₹)", min_value=1000, max_value=100000, value=14000)

    submitted = st.form_submit_button("Start Negotiation")

if submitted:
    run_negotiation_streamlit(
        product, market_price,
        buyer_name, buyer_personality, buyer_budget,
        seller_name, seller_personality, seller_min_price
    )
