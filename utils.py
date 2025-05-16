from datetime import datetime

# Convert blockTime (Unix timestamp) to human-readable time
def convert_block_time(block_time: int) -> str:
    # Convert the Unix timestamp to a datetime object
    return datetime.utcfromtimestamp(block_time).strftime('%Y-%m-%d %H:%M:%S UTC')

# Format Signatures into a readable response
def format_signatures(signatures: list) -> str:
    if isinstance(signatures, str):
        return "❌ No transaction signatures found."
    lines = []
    for sig in signatures:
        bt = convert_block_time(sig.get("blockTime", 0)) if sig.get("blockTime") else "N/A"
        lines.append(
            f"- Signature: {sig.get('signature','N/A')}, Block Time: {bt}, Slot: {sig.get('slot','N/A')}, Status: {sig.get('confirmationStatus','N/A')}"
        )
    return "\n".join(lines)


def format_account_info(account_info: dict) -> str:
    lamports = account_info.get("lamports", "N/A")
    executable = account_info.get("executable", "N/A")
    owner = account_info.get("owner", "N/A")
    rent_epoch = account_info.get("rentEpoch", "N/A")
    space = account_info.get("space", "N/A")

    return f"""
    📊 Account Info:
    - **Lamports**: {lamports} lamports (≈ {lamports / 1_000_000_000:.4f} SOL)
    - **Executable**: {executable}
    - **Owner**: {owner}
    - **Rent Epoch**: {rent_epoch}
    - **Space**: {space} bytes
    """