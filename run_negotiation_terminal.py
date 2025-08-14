import time
import random
import subprocess
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent

# =========================
# Existing BUYER_PERSONAS and SELLER_PERSONAS (kept for context)
BUYER_PERSONAS = { ... }  # Copy your existing dictionary
SELLER_PERSONAS = { ... }  # Copy your existing dictionary

# =========================
# LLaMA Helper
def call_llama(prompt):
    """
    Calls LLaMA 3.1:8b via ollama CLI and returns the generated text.
    """
    process = subprocess.Popen(
        ['ollama', 'run', 'llama3:8b'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(prompt)
    if stderr:
        print("LLaMA error:", stderr)
    return stdout.strip()

# =========================
# Buyer/Seller Turns with LLaMA integration
def buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message):
    buyer.observe_seller(seller_message)
    decision = buyer.decide(market_price)

    if round_num == 1:
        context = f"Buyer ({buyer_personality}) wants to start negotiation for {product} at market price ₹{market_price}."
    else:
        context = f"Buyer ({buyer_personality}) reacting to seller: '{seller_message}'"

    # Compose prompt for LLaMA
    prompt = f"{context}\nBuyer budget: ₹{buyer.budget}\nWhat should the buyer say or offer next?"
    message = call_llama(prompt)

    # Keep numeric offer for logic
    if decision['action'] in ["accept", "walk_away"]:
        offer = decision['offer']
    else:
        # Try to extract number from LLaMA output
        import re
        numbers = re.findall(r"\d+\.?\d*", message.replace(',', ''))
        offer = float(numbers[0]) if numbers else decision['offer']

    return {**decision, "offer": offer}, message

def seller_turn(seller, seller_personality, market_price, buyer_message):
    seller.observe_buyer(buyer_message)
    decision = seller.decide()

    context = f"Seller ({seller_personality}) reacting to buyer: '{buyer_message}'\nSeller minimum price: ₹{seller.cost_price}"
    prompt = f"{context}\nWhat should the seller say or offer next?"
    message = call_llama(prompt)

    # Keep numeric offer for logic
    import re
    numbers = re.findall(r"\d+\.?\d*", message.replace(',', ''))
    offer = float(numbers[0]) if numbers else decision['offer']

    return {**decision, "offer": offer}, message

# =========================
# Main Negotiation Loop
def run_negotiation(product, market_price, buyer_name, buyer_personality, buyer_budget,
                    seller_name, seller_personality, seller_min_price):
    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    seller_message = ""

    for round_num in range(1, 11):
        # BUYER TURN
        time.sleep(random.uniform(3, 6))
        buyer_decision, buyer_message = buyer_turn(round_num, buyer, buyer_personality, product, market_price, seller_message)
        print(f"{buyer_name} ({buyer_personality}): {buyer_message}")
        if buyer_decision['action'] in ["accept", "walk_away"]:
            print(f"Negotiation ended: {buyer_decision['action'].replace('_', ' ').title()}")
            break

        # SELLER TURN
        time.sleep(random.uniform(3, 6))
        seller_decision, seller_message = seller_turn(seller, seller_personality, market_price, buyer_message)
        print(f"{seller_name} ({seller_personality}): {seller_message}")
        if seller_decision['action'] in ["accept", "walk_away"]:
            print(f"Negotiation ended: {seller_decision['action'].replace('_', ' ').title()}")
            break

# =========================
# Console Input
if __name__ == "__main__":
    product = input("Enter product name: ")
    market_price = int(input("Enter market price (₹): "))

    buyer_name = input("Enter buyer name: ")
    buyer_personality = input("Enter buyer personality (Aggressive Trader, Diplomatic Buyer, Data-Driven Analyst, Creative Wildcard): ")
    buyer_budget = int(input("Enter buyer budget (₹): "))

    seller_name = input("Enter seller name: ")
    seller_personality = input("Enter seller personality (Aggressive Trader, Diplomatic Seller, Data-Driven Seller, Creative Wildcard): ")
    seller_min_price = int(input("Enter seller minimum price (₹): "))

    run_negotiation(
        product=product,
        market_price=market_price,
        buyer_name=buyer_name,
        buyer_personality=buyer_personality,
        buyer_budget=buyer_budget,
        seller_name=seller_name,
        seller_personality=seller_personality,
        seller_min_price=seller_min_price
    )
