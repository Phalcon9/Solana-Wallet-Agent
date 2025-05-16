import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
ALCHEMY_SOLANA_URL = os.getenv("ALCHEMY_SOLANA_URL")
ALCHEMY_DATA_API_URL = os.getenv("ALCHEMY_DATA_API_URL")

# Solana Balance Fetch Logic
async def get_solana_balance(wallet_address: str) -> float | str:
    payload = {
        "jsonrpc": "2.0",
        "method": "getBalance",
        "params": [wallet_address],
        "id": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ALCHEMY_SOLANA_URL, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if "result" in data and "value" in data["result"]:
                    lamports = data["result"]["value"]
                    return lamports / 1_000_000_000  # Convert to SOL
                return "Unavailable"
    except aiohttp.ClientError:
        return "Unavailable"


# Fetch Solana Account Info
async def get_account_info(wallet_address: str) -> dict | str:
    payload = {
        "jsonrpc": "2.0",
        "method": "getAccountInfo",
        "params": [wallet_address],
        "id": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ALCHEMY_SOLANA_URL, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if "result" in data and "value" in data["result"]:
                    account_info = data["result"]["value"]
                    return account_info
                return "Unavailable"
    except aiohttp.ClientError:
        return "Unavailable"


# Fetch Signatures for Address
async def get_signatures_for_address(wallet_address: str) -> list | str:
    payload = {
        "jsonrpc": "2.0",
        "method": "getSignaturesForAddress",
        "params": [wallet_address],
        "id": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ALCHEMY_SOLANA_URL, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if "result" in data:
                    return data["result"]
                return "Unavailable"
    except aiohttp.ClientError:
        return "Unavailable"


# New: Fetch Tokens By Wallet (async version)
async def get_tokens_by_wallet(wallet_address: str) -> dict | str:
    url = f"{ALCHEMY_DATA_API_URL}/assets/tokens/by-address"
    payload = {
        "addresses": [
            {
                "address": wallet_address,
                "networks": ["solana-mainnet"]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
        # Add API key headers here if required
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data
    except aiohttp.ClientError:
        return "Unavailable"
