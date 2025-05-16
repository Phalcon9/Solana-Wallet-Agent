# 🔐 Solana Wallet Assistant Agent

**Agent Address**: `agent1qguggk9tzfqzemqulwdukg8tmatt6ely8pm944jdks45fvql2x0l2aqa3fp`  
**Agent Name**: `Solana Wallet Activity Agent`

## 🧠 Overview

The **Solana Wallet Assistant Agent** is a conversational AI agent built using the [`uAgents`](https://github.com/fetchai/uAgents) framework. It provides intelligent insights into Solana wallet activity, token holdings, and transaction summaries. It integrates with the Alchemy Solana API and uses an LLM (like OpenAI) to generate user-friendly explanations.

---

## ⚙️ Features

- ✅ **SOL & Token Balance Checks**
- 📊 **Token Price and USD Valuation**
- 📜 **Wallet Transaction History (Last N Days)**
- 🧠 **AI-Powered Explanations for Wallet Balances**
- 💬 **Natural Language Chat Protocol with LLM Integration**
- 🧾 **Cached session support** for multi-step interactions

---

## 🚀 Agent Commands

| Command Example                                      | Description                                                  |
|------------------------------------------------------|--------------------------------------------------------------|
| `balance <wallet_address>`                           | Fetch SOL balance, token holdings, and current valuations.   |
| `What has my wallet done in the last 7 days?`        | Summary of recent transactions using AI.                     |
| `default`                                            | Standard explanation of wallet balance using LLM.            |
| _Any custom prompt_                                  | Get a personalized AI response based on wallet context.      |

---

## 🧬 Architecture

- **uAgents Framework** – Chat + Protocol agent
- **Alchemy Solana API** – Wallet, token, and signature data
- **LLM API** – Smart explanations and summaries
- **Async IO** – Fast non-blocking data fetches
- **Storage Layer** – Per-user context caching

---

## 🛠️ Setup Instructions

### 1. Clone this repo

```bash
git clone https://github.com/your-org/solana-balance-agent.git
cd solana-balance-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Environment Variables

Create a `.env` file or export environment variables as needed:

```env
ALCHEMY_SOLANA_URL=https://solana-mainnet.g.alchemy.com/v2/your-api-key
ALCHEMY_DATA_API_URL=https://api.g.alchemy.com/data/v1/your-api-key
```

> You may also need an `OPENAI_API_KEY` or equivalent for the LLM service in `llm.py`.

### 4. Run the Agent

```bash
python main_agent.py
```

---

## 📁 Project Structure

```plaintext
├── main_agent.py            # Agent logic and handlers
├── solana_request.py        # Async API calls to Alchemy
├── llm.py                   # LLM interaction module
├── utils.py                 # Formatting helpers
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## ✨ Example Output

```text
🔐 Wallet: 9xZ...23fB
💰 Balance: 0.5091 SOL

🪙 Tokens held

🔹 USDT
Balance: 32.500000 tokens
Market Price: $1.00
Wallet Balance: $32.50
------------------------------

Please send a custom prompt to explain this balance, or 'default' for an auto-generated explanation.
```

---

## 🤖 Acknowledgments

Built with:
- [uAgents Framework](https://github.com/fetchai/uAgents)
- [Alchemy Solana API](https://docs.alchemy.com/)
- [OpenAI / LLM APIs](https://platform.openai.com/docs)

---

## 📬 Contact

For support or contributions, reach out to the project maintainer at `tissan300@gmail.com`.
