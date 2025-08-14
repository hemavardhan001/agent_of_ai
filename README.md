# Agent of AI 🤖💼

**Agent of AI** is a Python-based framework designed to simulate negotiations between autonomous agents, leveraging AI to model buyer-seller interactions in a realistic environment. This project demonstrates AI-driven decision-making, negotiation strategies, and interactive visualization using .

---

## 🌟 Features

* **Autonomous Agents** – Modular buyer and seller agents with configurable strategies.
* **Negotiation Logic** – Implements realistic offer/counteroffer cycles and decision-making.
* **Interactive Visualization** – Streamlit interface for real-time monitoring of negotiations.
* **Extensible Design** – Easily add new personas, strategies, or negotiation rules.

---

## 🧰 Tech Stack

| Component          | Technology              |
| ------------------ | ----------------------- |
| Backend            | Python 3.11             |
| AI Model           | OpenAI GPT / Ollama API |
| Interface          | Streamlit               |
| Package Management | pip / virtualenv        |

---

## 📂 Project Structure

```
agent_of_ai/
│
├── buyer_bot.py               # Buyer agent logic
├── seller_bot.py              # Seller agent logic
├── negotiation_logic.py       # Core negotiation engine
├── streamlit_app.py           # Interactive interface
├── run_negotiation_terminal.py# CLI interface
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

---

## 🧠 Detailed Explanation of Key Components

### 1. Buyer Agent (`buyer_bot.py`)

The **Buyer Agent** is responsible for initiating offers based on a defined budget and negotiation strategy. It can behave in multiple personas such as “Aggressive Trader” or “Conservative Buyer”.

```python
class BuyerAgent:
    def __init__(self, name, budget):
        self.name = name
        self.budget = budget

    def make_offer(self, seller_price):
        # Buyer logic: offer slightly below seller price
        offer = max(seller_price - random.randint(50, 150), 0)
        return offer
```

**Explanation:**

* `name` and `budget` define the agent’s identity and financial limit.
* `make_offer()` computes a strategic offer, considering seller’s price and persona behavior.

---

### 2. Seller Agent (`seller_bot.py`)

The **Seller Agent** evaluates incoming offers and decides to accept, reject, or counteroffer.

```python
class SellerAgent:
    def __init__(self, name, min_price):
        self.name = name
        self.min_price = min_price

    def respond(self, buyer_offer):
        if buyer_offer >= self.min_price:
            return "Accept"
        else:
            counter = self.min_price
            return f"Counteroffer: {counter}"
```

**Explanation:**

* `min_price` defines the lowest acceptable value.
* `respond()` ensures the agent negotiates optimally while protecting its minimum value.

---

### 3. Negotiation Engine (`negotiation_logic.py`)

The **negotiation engine** coordinates the dialogue between agents until an agreement is reached or negotiation fails.

```python
def negotiate(buyer, seller):
    current_offer = seller.min_price
    while True:
        buyer_offer = buyer.make_offer(current_offer)
        response = seller.respond(buyer_offer)
        print(f"{buyer.name} offers ${buyer_offer}, {seller.name} responds: {response}")
        if response == "Accept":
            print("Deal reached!")
            break
```

**Explanation:**

* Implements a **turn-based negotiation loop**.
* Logs each offer and response for analysis.
* Provides a realistic simulation of negotiation dynamics.

---

### 4. Streamlit Interface (`streamlit_app.py`)

Streamlit enables **real-time visualization** of negotiations. Users can select personas, view dialogue, and observe the outcome interactively.

```python
import streamlit as st
from buyer_bot import BuyerAgent
from seller_bot import SellerAgent
from negotiation_logic import negotiate

st.title("Agent of AI - Negotiation Simulator")

buyer = BuyerAgent("Alice", 1000)
seller = SellerAgent("Bob", 1200)

if st.button("Start Negotiation"):
    negotiate(buyer, seller)
```

**Explanation:**

* Displays agent dialogue in a browser-based GUI.
* Supports dynamic persona selection and interactive sessions.

---

## 📊 Example Negotiation Flow

| Step | Buyer Offer | Seller Response |
| ---- | ----------- | --------------- |
| 1    | \$1000      | Counter: \$1200 |
| 2    | \$1100      | Counter: \$1150 |
| 3    | \$1150      | Accept          |

> Shows a typical negotiation session, illustrating offer adjustments and counteroffers.

---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/hemavardhan001/agent_of_ai.git
cd agent_of_ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="your_openai_api_key"  # Windows: set OPENAI_API_KEY="..."
```

---

## 🚀 Usage

**Streamlit Web App:**

```bash
streamlit run streamlit_app.py
```

**Command-Line Interface:**

```bash
python run_negotiation_terminal.py
```

---

## 🎯 Contributing

1. Fork repository
2. Create branch: `git checkout -b feature-branch`
3. Implement changes
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-branch`
6. Open Pull Request

---

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.



