import time
from negotiation_logic import run_negotiation

def cli_mode():
    print("\n=== Negotiation CLI Mode (Live Style) ===\n")

    # Input fields
    product = input("Product Name: ").strip()
    market_price = float(input("Market Price (₹): ").strip())
    buyer_name = input("Buyer Name: ").strip()
    buyer_personality = input(
        "Buyer Personality (Aggressive Trader, Diplomatic Buyer, Data-Driven Analyst, Creative Wildcard): "
    ).strip()
    buyer_budget = float(input("Buyer Maximum Price (₹): ").strip())
    seller_name = input("Seller Name: ").strip()
    seller_personality = input(
        "Seller Personality (Aggressive Trader, Diplomatic Seller, Data-Driven Seller, Creative Wildcard): "
    ).strip()
    seller_min_price = float(input("Seller Minimum Price (₹): ").strip())

    # Run negotiation (removed unsupported args)
    result = run_negotiation(
        product, market_price,
        buyer_name, buyer_personality, buyer_budget,
        seller_name, seller_personality, seller_min_price
    )

    print("\n=== Negotiation Conversation (Live) ===")
    current_round = None

    for h in result['history']:
        # New round delay
        if h['round'] != current_round:
            # Simulate thinking time — slower early, faster later
            delay = 1.5 if h['round'] < 5 else 1.0 if h['round'] < 8 else 0.6
            time.sleep(delay)
            print(f"\n--- Round {h['round']} ---")
            current_round = h['round']

        # Typing effect for message
        prefix = f"{h['speaker']} ({h['personality']}): "
        print(prefix, end="", flush=True)
        for char in h['message']:
            print(char, end="", flush=True)
            time.sleep(0.015)  # Speed of "typing"
        print()  # new line after message

    # Show final result
    time.sleep(0.8)
    print("\n=== Negotiation Result ===")
    print(f"Status: {result['status']}")
    if 'price' in result:
        print(f"Final Price: ₹{result['price']}")

if __name__ == "__main__":
    cli_mode()
