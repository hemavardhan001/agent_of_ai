import streamlit as st
import random
import time
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent

# =========================
# Buyer and Seller Personas
BUYER_PERSONAS = {
    "Aggressive Trader": {
        "openers": [
            "Alright, listen. I don’t have time to waste—what’s your rock-bottom price for {product}?",
            "Skip the small talk—how much for {product}?"
        ],
        "counter": [
            "Too high. Knock at least ₹{} off and maybe we’ll talk.",
            "You’re not serious with that price—how about ₹{}?"
        ],
        "accepts": ["Fine. Done.", "Alright, you’ve got a deal."],
        "walks": ["Forget it, I’m out.", "Not worth my time."]
    },
    "Diplomatic Buyer": {
        "openers": [
            "Hi! I’m really interested in {product}, and I hope we can agree on something fair.",
            "Hello there, I’ve had my eye on {product} for a while."
        ],
        "counter": [
            "I understand your position, but would you consider ₹{}?",
            "I think we can both be happy at ₹{}."
        ],
        "accepts": ["That works for me. Deal!", "Perfect, let’s do it."],
        "walks": ["I appreciate your time, but I’ll have to pass.", "Maybe another time."]
    },
    "Data-Driven Analyst": {
        "openers": [
            "Based on my market checks, {product} usually sells for around ₹{market_price}.",
            "I’ve reviewed the trends, and ₹{market_price} is the standard rate for {product}."
        ],
        "counter": [
            "Statistically, ₹{} is a fair midpoint.",
            "Given current demand, ₹{} makes more sense."
        ],
        "accepts": ["The math checks out. Deal.", "Data aligns, I’m in."],
        "walks": ["Numbers don’t fit, so I’ll pass.", "Not in my target range."]
    },
    "Creative Wildcard": {
        "openers": [
            "Imagine if {product} was the crown jewel of my collection—what would be your magical price?",
            "I dreamed about {product} last night—it told me it’s worth ₹{market_price}!"
        ],
        "counter": [
            "What if we meet at ₹{}—I’ll throw in good vibes for free.",
            "₹{} feels like destiny to me."
        ],
        "accepts": ["That’s poetic enough for me. Deal!", "We’ve painted the perfect picture—done."],
        "walks": ["The stars don’t align today.", "Not feeling it anymore."]
    }
}

SELLER_PERSONAS = {
    "Aggressive Trader": [
        "Price is firm. ₹{}—take it or leave it.",
        "Someone else will take it for ₹{}, don’t waste time."
    ],
    "Diplomatic Seller": [
        "I understand, but how about ₹{}?",
        "Let’s try to meet halfway—₹{}."
    ],
    "Data-Driven Seller": [
        "Market data says ₹{} is already competitive.",
        "Based on supply and demand, I can do ₹{}."
    ],
    "Creative Wildcard": [
        "₹{}—and I’ll wrap it in gold paper for you.",
        "₹{} feels like fate."
    ]
}

# =========================
# Helper: Typing effect
def stream_typing_effect(text, delay=0.03):
    """Simulate typing animation in Streamlit."""
    placeholder = st.empty()
    displayed = ""
    for char in text:
        displayed += char
        placeholder.markdown(displayed)
        time.sleep(delay)
    return placeholder

# =========================
# Turn Handlers
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

def seller_turn(seller, seller_personality, market_price, buyer_message):
    seller.observe_buyer(buyer_message)
    decision = seller.decide()
    persona = SELLER_PERSONAS[seller_personality]

    if decision['action'] == "accept":
        message = "We have a deal!"
    elif decision['action'] == "walk_away":
        message = "I can’t go lower—good luck."
    else:
        message = random.choice(persona).format(decision['offer'])

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
        buyer_decision, buyer_message = buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message)
        history.append({
            "round": round_num,
            "speaker": buyer_name,
            "personality": buyer_personality,
            "message": buyer_message,
            "action": buyer_decision['action'],
            "offer": buyer_decision['offer']
        })
        if buyer_decision['action'] in ["accept", "walk_away"]:
            return {"status": "Deal Reached" if buyer_decision['action']=="accept" else "No Deal",
                    "price": buyer_decision['offer'], "history": history}

        # SELLER TURN
        seller_decision, seller_message = seller_turn(seller, seller_personality, market_price, buyer_message)
        history.append({
            "round": round_num,
            "speaker": seller_name,
            "personality": seller_personality,
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
    st.title("🤝 AI Negotiation Simulator")

    product = st.text_input("Product", "Smartphone")
    market_price = st.number_input("Market Price (₹)", 1000, 100000, 15000)
    buyer_name = st.text_input("Buyer Name", "Alice")
    buyer_personality = st.selectbox("Buyer Personality", list(BUYER_PERSONAS.keys()))
    buyer_budget = st.number_input("Buyer Budget (₹)", 1000, 100000, 16000)

    seller_name = st.text_input("Seller Name", "Bob")
    seller_personality = st.selectbox("Seller Personality", list(SELLER_PERSONAS.keys()))
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
            time.sleep(0.8)  # Pause between turns

        if result["status"] == "Deal Reached":
            st.success(f"🎉 Deal reached at ₹{int(round(result['price'])):,}!")
        elif result["status"] == "No Deal":
            st.warning("Negotiation ended with no deal.")
        else:
            st.info("No deal after max rounds.")

if __name__ == "__main__":
    main()
