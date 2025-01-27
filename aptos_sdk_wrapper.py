print("Aptos SDK wrapper loaded in test mode")
import os
import requests
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.transactions import EntryFunction, TransactionArgument, TransactionPayload
from aptos_sdk.bcs import Serializer

# Initialize clients for devnet (changed from testnet)
NODE_URL = "https://api.devnet.aptoslabs.com/v1"
rest_client = RestClient(NODE_URL)
faucet_client = FaucetClient("https://faucet.devnet.aptoslabs.com", rest_client)

async def get_account_modules(address: str, limit: int = 10):
    """
    Fetch the published modules for a specific account,
    capping the results at 'limit' to avoid large GPT-4 prompts.
    """
    import requests
    
    # Add '?limit={limit}' for server-side pagination.
    # Then if the account has more than 'limit' modules, the server might
    # provide an "X-Aptos-Cursor" header for further pages (if needed).
    url = f"{NODE_URL}/accounts/{address}/modules?limit={limit}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        modules = response.json()

        if not modules:
            return "No modules found for this account"

        # Summarize or truncate large data fields inside each module
        summarized_modules = []
        for m in modules:
            # We might remove or shorten 'bytecode' if it's huge
            if "bytecode" in m:
                byte_len = len(m["bytecode"])
                if byte_len > 300:
                    m["bytecode"] = (
                        m["bytecode"][:300]
                        + f"...(truncated {byte_len-300} chars)"
                    )

            # Possibly parse 'abi' and only keep minimal info
            # to prevent huge text from each function signature
            if "abi" in m:
                abi = m["abi"]
                # Example: remove generics if you don't need them
                if "exposed_functions" in abi:
                    for fn in abi["exposed_functions"]:
                        # Remove or shorten params if super large
                        if "params" in fn and len(fn["params"]) > 5:
                            fn["params"] = fn["params"][:5] + ["...truncated"]
            
            summarized_modules.append(m)

        # If the server truncated results to 'limit' behind the scenes,
        # you might want to add a note. You can glean if there's more from
        # the "X-Aptos-Cursor" header, but let's keep it simple:
        return {
            "modules": summarized_modules,
            "note": (
                f"Requested up to {limit} modules. "
                "Large fields were truncated to prevent large GPT-4 prompts."
            )
        }

    except requests.exceptions.RequestException as e:
        return f"Error getting account modules: {str(e)}"

async def execute_view_function(function_id: str, type_args: list, args: list):
    """Executes a Move view function."""
    url = "https://api.devnet.aptoslabs.com/v1/view"
    headers = {"Content-Type": "application/json"}
    body = {
        "function": function_id,
        "type_arguments": type_args,
        "arguments": args
    }

    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error calling view function: {str(e)}"

async def fund_wallet(wallet_address, amount):
    """Funds a wallet with a specified amount of APT."""
    print(f"Funding wallet: {wallet_address} with {amount} APT")
    amount = int(amount)
    if amount > 1000:
        raise ValueError(
            "Amount too large. Please specify an amount less than 1000 APT")
    octas = amount * 10**8  # Convert APT to octas
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    txn_hash = await faucet_client.fund_account(wallet_address, octas, True)
    print(f"Transaction hash: {txn_hash}\nFunded wallet: {wallet_address}")
    return wallet_address

async def get_balance(wallet_address):
    """Retrieves the balance of a specified wallet."""
    print(f"Getting balance for wallet: {wallet_address}")
    if isinstance(wallet_address, str):
        wallet_address = AccountAddress.from_str(wallet_address)
    balance = await rest_client.account_balance(wallet_address)
    balance_in_apt = balance / 10**8  # Convert octas to APT
    print(f"Wallet balance: {balance_in_apt:.2f} APT")
    return balance

async def transfer(sender: Account, receiver, amount):
    """Transfers a specified amount from sender to receiver."""
    if isinstance(receiver, str):
        receiver = AccountAddress.from_str(receiver)
    txn_hash = await rest_client.bcs_transfer(sender, receiver, amount)
    print(f"Transaction hash: {txn_hash} and receiver: {receiver}")
    return txn_hash

async def get_transaction(txn_hash: str):
    """Gets details about a specific transaction."""
    try:
        result = await rest_client.transaction_by_hash(txn_hash)
        return result
    except Exception as e:
        print(f"Full error: {str(e)}")
        return f"Error getting transaction: {str(e)}"

import requests

async def get_account_resources(address: str):
    """Gets all resources associated with an account using direct API call."""
    NODE_URL = "https://api.devnet.aptoslabs.com/v1"  # Update for the correct network
    try:
        # Use direct API call to fetch resources
        url = f"{NODE_URL}/accounts/{address}/resources"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        resources = response.json()
        if not resources:
            return "No resources found for this account"
        return resources
    except requests.exceptions.RequestException as e:
        return f"Error getting account resources: {str(e)}"

async def get_token_balance(address: str, creator_address: str, collection_name: str, token_name: str):
    """Gets the token balance for a specific token."""
    try:
        if isinstance(address, str):
            address = AccountAddress.from_str(address)
        resources = await rest_client.get_account_resources(address)
        for resource in resources:
            if resource['type'] == '0x3::token::TokenStore':
                # Parse token data to find specific token balance
                tokens = resource['data']['tokens']
                token_id = f"{creator_address}::{collection_name}::{token_name}"
                if token_id in tokens:
                    return tokens[token_id]
        return "Token not found"
    except Exception as e:
        return f"Error getting token balance: {str(e)}"

async def create_token(sender: Account, name: str, symbol: str, icon_uri: str,
                       project_uri: str):
    """Creates a token with specified attributes."""
    print(
        f"Creating FA with name: {name}, symbol: {symbol}, icon_uri: {icon_uri}, project_uri: {project_uri}"
    )
    payload = EntryFunction.natural(
        "0xe522476ab48374606d11cc8e7a360e229e37fd84fb533fcde63e091090c62149::launchpad",
        "create_fa_simple",
        [],
        [
            TransactionArgument(name, Serializer.str),
            TransactionArgument(symbol, Serializer.str),
            TransactionArgument(icon_uri, Serializer.str),
            TransactionArgument(project_uri, Serializer.str),
        ])
    signed_transaction = await rest_client.create_bcs_signed_transaction(
        sender, TransactionPayload(payload))
    txn_hash = await rest_client.submit_bcs_transaction(signed_transaction)
    print(f"Transaction hash: {txn_hash}")
    return txn_hash