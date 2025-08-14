import time
import random
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent

# Your existing BUYER_PERSONAS and SELLER_PERSONAS dictionaries here (copy exactly)
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


def run_negotiation(product, market_price, buyer_name, buyer_personality, buyer_budget,
                    seller_name, seller_personality, seller_min_price):

    buyer = BuyerAgent(buyer_name, buyer_personality, buyer_budget)
    seller = SellerAgent(seller_name, seller_personality, seller_min_price)

    seller_message = ""

    for round_num in range(1, 11):
        # BUYER TURN
        time.sleep(random.uniform(3, 6))  # realistic typing delay
        buyer_decision, buyer_message = buyer_turn(
            round_num, buyer, buyer_personality, product, market_price, seller_message
        )
        print(f"{buyer_name} ({buyer_personality}): {buyer_message}")
        if buyer_decision['action'] in ["accept", "walk_away"]:
            print(f"Negotiation ended: {buyer_decision['action'].replace('_', ' ').title()}")
            break

        # SELLER TURN
        time.sleep(random.uniform(3, 6))  # realistic typing delay
        seller_decision, seller_message = seller_turn(
            seller, seller_personality, market_price, buyer_message
        )
        print(f"{seller_name} ({seller_personality}): {seller_message}")
        if seller_decision['action'] in ["accept", "walk_away"]:
            print(f"Negotiation ended: {seller_decision['action'].replace('_', ' ').title()}")
            break

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

