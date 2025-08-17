import time
import random
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent

# =========================
# Typing simulation for realistic dialogue
def simulate_typing(message: str, min_delay=0.01, max_delay=0.03):
    """Simulate human typing with random speed per character."""
    for char in message:
        print(char, end="", flush=True)
        time.sleep(random.uniform(min_delay, max_delay))
    print()

# =========================
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

# =========================
# Seller Turn (fixed for profit)
def seller_turn(seller, last_buyer_offer):
    seller.observe_buyer(str(last_buyer_offer))
    # Start higher than buyer's last offer or at least 20% above min_price
    start_offer = max(seller.min_price * 1.2, last_buyer_offer + 500 if last_buyer_offer else seller.min_price * 1.5)
    # Gradual decrease toward buyer, never below min_price
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

# =========================
# Main Negotiation Loop
def run_negotiation(product, market_price, buyer_name, buyer_personality, buyer_budget,
                    seller_name, seller_personality, seller_min_price):
    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    last_buyer_offer = 0
    last_seller_offer = 0
    final_price = 0

    print(f"\nNegotiation started for {product} (Market Price ₹{market_price})!\n")

    for round_num in range(1, 13):  # Max 12 rounds
        print(f"--- Round {round_num} ---")

        # Buyer Turn
        buyer_decision, buyer_message = buyer_turn(buyer, last_seller_offer)
        last_buyer_offer = buyer_decision["offer"]
        simulate_typing(f"{buyer_name} ({buyer_personality}): {buyer_message} (Offer: ₹{int(last_buyer_offer)})")

        # Seller Turn
        seller_decision, seller_message = seller_turn(seller, last_buyer_offer)
        last_seller_offer = seller_decision["offer"]
        simulate_typing(f"{seller_name} ({seller_personality}): {seller_message} (Offer: ₹{int(last_seller_offer)})\n")

        # Check if deal close enough
        if abs(last_seller_offer - last_buyer_offer) <= 1000:
            final_price = int((last_seller_offer + last_buyer_offer) / 2)
            break

        time.sleep(0.2)  # conversation speed

    # Force deal if max rounds reached
    if final_price == 0:
        final_price = int((last_seller_offer + last_buyer_offer) / 2)

    # =========================
    # Calculate profit for both
    buyer_profit = max(0, buyer_budget - final_price)
    seller_profit = max(0, final_price - seller_min_price)

    # Determine winner
    if buyer_profit > seller_profit:
        winner = f"{buyer_name} ({buyer_personality}) got better deal"
    elif seller_profit > buyer_profit:
        winner = f"{seller_name} ({seller_personality}) got better deal"
    else:
        winner = "Both parties negotiated fairly"

    # =========================
    # Final Result
    print(f"\n✅ DEAL SUCCESS! Final Agreed Price: ₹{final_price}")
    print(f"Buyer Profit: ₹{buyer_profit}")
    print(f"Seller Profit: ₹{seller_profit}")
    print(f"Winner: {winner}\n")

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
