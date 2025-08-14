import streamlit as st
import random
import time
from buyer_bot import BuyerAgent  # Updated with LLaMA inside
from seller_bot import SellerAgent  # Updated with LLaMA inside
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# =========================
# Helper: Typing effect
def stream_typing_effect(text, delay=0.03):
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed)
        time.sleep(delay)
    return placeholder

# =========================
# Turn Handlers with LLaMA-generated messages
def buyer_turn(round_num, buyer, product, market_price):
    decision = buyer.decide(market_price)

    if round_num == 1:
        prompt = f"""
        You are a Buyer AI with personality: {buyer.personality_type}.
        You are starting negotiation for {product} at market price ₹{market_price}.
        Generate a natural, polite, concise opening message.
        """
    elif decision['action'] == "accept":
        prompt = f"""
        You are a Buyer AI with personality: {buyer.personality_type}.
        Seller offered ₹{buyer.latest_seller_offer}.
        You accept the offer. Respond naturally, politely, and concisely.
        """
    elif decision['action'] == "walk_away":
        prompt = f"""
        You are a Buyer AI with personality: {buyer.personality_type}.
        You cannot agree to the seller's offer of ₹{buyer.latest_seller_offer}.
        Politely walk away from negotiation in 1–2 sentences.
        """
    else:
        prompt = f"""
        You are a Buyer AI with personality: {buyer.personality_type}.
        Seller offered ₹{buyer.latest_seller_offer}.
        You want to counteroffer ₹{decision['offer']}.
        Respond naturally, politely, and concisely in 1–2 sentences.
        """

    formatted_prompt = ChatPromptTemplate.from_template("{prompt}").format(prompt=prompt)
    message = buyer.llm.invoke(formatted_prompt).content
    return decision, message

def seller_turn(seller):
    decision = seller.decide()

    if decision['action'] == "accept":
        prompt = f"""
        You are a Seller AI with personality: {seller.personality_type}.
        Buyer offered ₹{seller.latest_buyer_offer}.
        You accept the offer. Respond naturally, politely, and concisely.
        """
    elif decision['action'] == "walk_away":
        prompt = f"""
        You are a Seller AI with personality: {seller.personality_type}.
        Buyer offered ₹{seller.latest_buyer_offer}.
        You cannot agree. Politely walk away from negotiation in 1–2 sentences.
        """
    else:
        prompt = f"""
        You are a Seller AI with personality: {seller.personality_type}.
        Buyer offered ₹{seller.latest_buyer_offer}.
        You counteroffer ₹{decision['offer']}.
        Respond naturally, politely, and concisely in 1–2 sentences.
        """

    formatted_prompt = ChatPromptTemplate.from_template("{prompt}").format(prompt=prompt)
    message = seller.llm.invoke(formatted_prompt).content
    return decision, message

# =========================
# Main Negotiation Loop
def run_negotiation(product, market_price, buyer_name, buyer_personality, buyer_budget,
                    seller_name, seller_personality, seller_min_price):

    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    history = []
    seller_message = ""

    for round_num in range(1, 11):
        # BUYER TURN
        buyer.observe_seller(seller_message)
        buyer_decision, buyer_message = buyer_turn(round_num, buyer, product, market_price)
        history.append({
            "round": round_num,
            "speaker": buyer_name,
            "personality": buyer.personality_type,
            "message": buyer_message,
            "action": buyer_decision['action'],
            "offer": buyer_decision['offer']
        })
        if buyer_decision['action'] in ["accept", "walk_away"]:
            return {"status": "Deal Reached" if buyer_decision['action']=="accept" else "No Deal",
                    "price": buyer_decision['offer'], "history": history}

        # SELLER TURN
        seller.observe_buyer(buyer_message)
        seller_decision, seller_message = seller_turn(seller)
        history.append({
            "round": round_num,
            "speaker": seller_name,
            "personality": seller.personality_type,
            "message": seller_message,
            "action": seller_decision['action'],
            "offer": seller_decision['offer']
        })
        if seller_decision['action'] in ["accept", "walk_away"]:
            return {"status": "Deal Reached" if seller_decision['action']=="accept" else "No Deal",
                    "price": seller_decision['offer'], "history": history}

    return {"status": "No Deal After Max Rounds", "history": history}

# =========================
# Streamlit UI
def main():
    st.title("🤝 AI Negotiation Simulator with LLaMA 3.1:8b")

    product = st.text_input("Product", "Smartphone")
    market_price = st.number_input("Market Price (₹)", 1000, 100000, 15000)
    buyer_name = st.text_input("Buyer Name", "Alice")
    buyer_personality = st.selectbox("Buyer Personality", ["Aggressive Negotiator", "Diplomatic Buyer", "Data Analyst", "Creative Wildcard"])
    buyer_budget = st.number_input("Buyer Budget (₹)", 1000, 100000, 16000)

    seller_name = st.text_input("Seller Name", "Bob")
    seller_personality = st.selectbox("Seller Personality", ["Aggressive Trader", "Diplomatic Seller", "Data-Driven Seller", "Creative Wildcard"])
    seller_min_price = st.number_input("Seller Minimum Price (₹)", 1000, 100000, 14000)

    if st.button("Start Negotiation"):
        result = run_negotiation(
            product, market_price, buyer_name, buyer_personality, buyer_budget,
            seller_name, seller_personality, seller_min_price
        )

        st.markdown("### Negotiation History")
        for turn in result["history"]:
            with st.chat_message("assistant" if turn['speaker'] == seller_name else "user"):
                stream_typing_effect(f"**{turn['speaker']} ({turn['personality']}):** {turn['message']}")
            time.sleep(0.8)

        if result["status"] == "Deal Reached":
            st.success(f"🎉 Deal reached at ₹{int(round(result['price'])):,}!")
        elif result["status"] == "No Deal":
            st.warning("Negotiation ended with no deal.")
        else:
            st.info("No deal after max rounds.")

if __name__ == "__main__":
    main()
