import re
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents_core.models import ErrorMessage
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec,
)

from solana_request import (
    get_account_info,
    get_solana_balance,
    get_signatures_for_address,
    get_tokens_by_wallet,
)
from llm import get_completion
from utils import convert_block_time, format_signatures, format_account_info

# Setup Protocol and Agent
chat_proto = Protocol(spec=chat_protocol_spec)
agent = Agent()

def is_valid_wallet_address(address: str) -> bool:
    return bool(address) and 30 <= len(address) <= 44

async def fetch_wallet_data(wallet_address: str):
    try:
        sol_balance, account_info, signatures = await asyncio.gather(
            get_solana_balance(wallet_address),
            get_account_info(wallet_address),
            get_signatures_for_address(wallet_address),
        )
    except Exception as e:
        return None, f"Error fetching wallet data: {str(e)}"

    if isinstance(sol_balance, str) or isinstance(account_info, str) or isinstance(signatures, str):
        return None, "Could not fetch complete data for this wallet. Please check the address."

    return {
        "wallet_address": wallet_address,
        "sol_balance": sol_balance,
        "account_info": account_info,
        "signatures": signatures,
    }, None

async def generate_custom_explanation(prompt_text: str):
    explanation = await get_completion(
        context="You are an expert Solana assistant that explains wallet balances to users.",
        prompt=prompt_text
    )
    return explanation["choices"][0]["message"]["content"]

async def generate_activity_summary(filtered_sigs, days: int):
    formatted_sigs = format_signatures(filtered_sigs)
    llm_prompt = (
        f"Summarize the wallet's transaction activity in the last {days} days based on these transactions:\n"
        f"{formatted_sigs}"
    )
    try:
        llm_response = await get_completion(
            context="You are an expert Solana assistant summarizing wallet activities.",
            prompt=llm_prompt,
        )
        summary_text = llm_response["choices"][0]["message"]["content"]
    except Exception:
        summary_text = "Unable to generate detailed summary at this time."
    return formatted_sigs, summary_text

def generate_token_summary(tokens_data) -> str:
    if tokens_data == "Unavailable" or not tokens_data.get("data") or not tokens_data["data"].get("tokens"):
        return "No tokens found."

    tokens_list = tokens_data["data"]["tokens"]
    token_lines = []

    for token in tokens_list:
        token_address = token.get("tokenAddress") or "SOL (native)"
        token_name = token_address  # default to address if no metadata available

        balance_hex = token.get("tokenBalance", "0x0")
        try:
            balance_int = int(balance_hex, 16)
            if token_address == "SOL (native)":
                balance_val = balance_int / 1_000_000_000
                balance_display = f"{balance_val:.6f} SOL"
            else:
                balance_val = balance_int / 1_000_000
                balance_display = f"{balance_val:.6f} tokens"
        except Exception:
            balance_display = "0"

        price_info = token.get("tokenPrices", [])
        price_str = "N/A"
        usd_value = "N/A"
        if price_info:
            price = float(price_info[0]['value'])
            price_str = f"${price:.2f}"
            usd_value = f"${balance_val * price:.4f}"

        token_lines.append(f"🔹 {token_name}\n\nBalance: {balance_display}\n\nMarket Price: {price_str}\n\nWallet Balance: {usd_value}\n\n{'-'*30}")

    return "\n".join(token_lines)

@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(f"✅ Solana Balance Agent started at: {agent.address}")

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    text = msg.content[0].text.strip()
    ctx.logger.info(f"📨 Message received from {sender}: {text}")
    lower_text = text.lower()

    def make_msg(text: str) -> ChatMessage:
        return ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[TextContent(type="text", text=text)]
        )

    if lower_text.startswith("balance "):
        wallet_address = text.split(" ", 1)[1].strip()
        if not is_valid_wallet_address(wallet_address):
            await ctx.send(sender, make_msg("❌ Invalid wallet address format. Please try again."))
            return

        wallet_data, tokens_data = None, None
        error = None
        try:
            wallet_data_task = fetch_wallet_data(wallet_address)
            tokens_data_task = get_tokens_by_wallet(wallet_address)
            wallet_data, error = await wallet_data_task
            tokens_data = await tokens_data_task
        except Exception as e:
            await ctx.send(sender, make_msg(f"❌ Error fetching wallet info: {str(e)}"))
            return

        if error:
            await ctx.send(sender, make_msg(f"❌ {error}"))
            return

        tokens_summary = generate_token_summary(tokens_data)

        ctx.storage.set(f"wallet_info_{sender}", wallet_data)

        response = (
            f"🔐 Wallet: `{wallet_address}`\n"
            f"💰 Balance: `{wallet_data['sol_balance']:.4f} SOL`\n\n"
            f"🪙 Tokens held \n\n"
            f" \n{tokens_summary}\n\n"
            "Please send me a custom prompt to explain this balance, "
            "or send 'default' to use the standard explanation.\n"
            "You can also ask about your wallet activity, e.g., 'What has my wallet done in the last 7 days?'"
        )
        await ctx.send(sender, make_msg(response))
        return

    cached = ctx.storage.get(f"wallet_info_{sender}")
    if not cached:
        await ctx.send(sender, make_msg("⚠️ Please send a wallet address first using: balance <wallet_address>"))
        return

    activity_keywords = [
        "what has my wallet done",
        "recent activity",
        "transactions in last",
        "wallet activity",
        "activity in the last",
        "wallet history"
    ]
    days_match = re.search(r"last\s+(\d+)\s+days", lower_text)
    if any(keyword in lower_text for keyword in activity_keywords) and days_match:
        days = int(days_match.group(1))
        since_time = datetime.utcnow() - timedelta(days=days)

        filtered_sigs = []
        for sig in cached["signatures"]:
            block_time = sig.get("blockTime")
            if block_time:
                sig_time = datetime.utcfromtimestamp(block_time)
                if sig_time >= since_time:
                    filtered_sigs.append(sig)

        if not filtered_sigs:
            await ctx.send(sender, make_msg(f"ℹ️ No transactions found in the last {days} days."))
            return

        formatted_sigs, summary_text = await generate_activity_summary(filtered_sigs, days)

        response = (
            f"🗓️ Wallet activity in the last {days} days:\n\n"
            f"{formatted_sigs}\n\n"
            f"🧠 AI Summary:\n{summary_text}"
        )
        await ctx.send(sender, make_msg(response))
        return

    prompt_text = text
    if lower_text == "default":
        prompt_text = f"What does it mean for a user to have {cached['sol_balance']:.4f} SOL in their wallet?"

    explanation_text = await generate_custom_explanation(prompt_text)

    response = (
        f"🧠 AI Explanation based on your prompt:\n\n"
        f"{explanation_text}\n\n"
        f"📝 Account Info:\n{format_account_info(cached['account_info'])}\n\n"
        f"📝 Transaction Signatures:\n{format_signatures(cached['signatures'])}"
    )
    await ctx.send(sender, make_msg(response))

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"✅ Acknowledged message ID: {msg.acknowledged_msg_id} from {sender}")

agent.include(chat_proto, publish_manifest=True)

# Uncomment to run locally
# if __name__ == "__main__":
#     agent.run()
