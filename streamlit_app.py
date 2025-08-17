import streamlit as st
import time
import random
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent

# ------------------------
# Typing simulation for Streamlit (live effect)
def simulate_typing(message: str):
    placeholder = st.empty()  # placeholder to update text
    displayed_text = ""
    for char in message:
        displayed_text += char
        placeholder.text(displayed_text)
        time.sleep(random.uniform(0.02, 0.06))  # live typing speed

# ------------------------
# Buyer Turn
def buyer_turn(buyer, last_seller_offer):
    buyer.observe_seller(str(last_seller_offer))
    start_offer = buyer.budget * 0.8
    if last_seller_offer > 0:
        increment = (last_seller_offer - start_offer) * 0.3
        offer = min(buyer.budget, start_offer + increment)
    else:
        offer = start_offer

    messages = [
        f"I can give you ₹{int(offer)}, what do you say?",
        f"My best is ₹{int(offer)}, can we agree?",
        f"I can offer ₹{int(offer)}, take it or leave it.",
        f"How about ₹{int(offer)}?"
    ]
    message = random.choice(messages)
    return {"offer": offer}, message

# ------------------------
# Seller Turn
def seller_turn(seller, last_buyer_offer):
    seller.observe_buyer(str(last_buyer_offer))
    start_offer = max(seller.min_price * 1.2, last_buyer_offer + 500 if last_buyer_offer else seller.min_price * 1.5)
    if last_buyer_offer < start_offer:
        offer = max(seller.min_price * 1.1, start_offer - random.randint(500, 1500))
    else:
        offer = max(seller.min_price, start_offer - random.randint(500, 1500))

    messages = [
        f"I can do ₹{int(offer)}, that's my offer.",
        f"₹{int(offer)} is fair, can we agree?",
        f"My price is ₹{int(offer)}, take it or leave it.",
        f"How about ₹{int(offer)}?"
    ]
    message = random.choice(messages)
    return {"offer": offer}, message

# ------------------------
# Streamlit UI
st.title("Buyer-Seller Negotiation Simulator")

# User Inputs
product = st.text_input("Product Name", "Laptop")
market_price = st.number_input("Market Price (₹)", value=50000)

buyer_name = st.text_input("Buyer Name", "Alice")
buyer_personality = st.selectbox(
    "Buyer Personality", 
    ["Aggressive Trader", "Diplomatic Buyer", "Data-Driven Analyst", "Creative Wildcard"]
)
buyer_budget = st.number_input("Buyer Budget (₹)", value=40000)

seller_name = st.text_input("Seller Name", "Bob")
seller_personality = st.selectbox(
    "Seller Personality", 
    ["Aggressive Trader", "Diplomatic Seller", "Data-Driven Seller", "Creative Wildcard"]
)
seller_min_price = st.number_input("Seller Minimum Price (₹)", value=35000)

# ------------------------
# Start Negotiation
if st.button("Start Negotiation"):
    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    last_buyer_offer = 0
    last_seller_offer = 0
    final_price = 0

    st.subheader(f"Negotiation started for {product} (Market Price ₹{market_price})")

    # Time-based negotiation (100 - 120 seconds)
    start_time = time.time()
    max_time = random.randint(100, 120)  # random duration in seconds
    round_num = 1

    while time.time() - start_time < max_time:
        st.markdown(f"### Round {round_num}")

        # Buyer Turn
        buyer_decision, buyer_message = buyer_turn(buyer, last_seller_offer)
        last_buyer_offer = buyer_decision["offer"]
        simulate_typing(f"{buyer_name} ({buyer_personality}): {buyer_message} (Offer: ₹{int(last_buyer_offer)})")

        # Seller Turn
        seller_decision, seller_message = seller_turn(seller, last_buyer_offer)
        last_seller_offer = seller_decision["offer"]
        simulate_typing(f"{seller_name} ({seller_personality}): {seller_message} (Offer: ₹{int(last_seller_offer)})")

        # Check if deal is close enough
        if abs(last_seller_offer - last_buyer_offer) <= 1000:
            final_price = int((last_seller_offer + last_buyer_offer) / 2)
            break

        round_num += 1

    # If no deal within time, take midpoint of last offers
    if final_price == 0:
        final_price = int((last_seller_offer + last_buyer_offer) / 2)

    # Profit & Winner
    buyer_profit = max(0, buyer_budget - final_price)
    seller_profit = max(0, final_price - seller_min_price)

    if buyer_profit > seller_profit:
        winner = f"{buyer_name} ({buyer_personality}) got better deal"
    elif seller_profit > buyer_profit:
        winner = f"{seller_name} ({seller_personality}) got better deal"
    else:
        winner = "Both parties negotiated fairly"

    # Display Final Result
    st.success(f"✅ DEAL SUCCESS! Final Agreed Price: ₹{final_price}")
    st.info(f"Buyer Profit: ₹{buyer_profit}  |  Seller Profit: ₹{seller_profit}  |  Winner: {winner}")
