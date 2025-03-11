import os
import json
import asyncio
import requests
from dotenv import load_dotenv
from requests_oauthlib import OAuth1
from aptos_sdk.account import Account
from aptos_sdk_wrapper import (
    get_balance, fund_wallet, transfer, create_token,
    get_transaction, get_account_resources, get_token_balance, execute_view_function, execute_entry_function, get_account_modules, 
)
from crewai import Agent  # Replaced Swarm with Crew AI
from typing import List

# Load environment variables first!
load_dotenv()

# Initialize the event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize test wallet
wallet = Account.generate()  # TODO: You can update this with your account if you want an agent with a specific address on-chain using Account.load_key('...')
address = str(wallet.address())

def get_user_wallet():
    return os.getenv('DEVNET_WALLET_ADDRESS')

def get_balance_in_apt_sync(address=None):
    """Get balance for an address or default to user's or agent's address."""
    try:
        target_address = address if address else get_user_wallet() or str(wallet.address())
        return loop.run_until_complete(get_balance(target_address))
    except Exception as e:
        return f"Error getting balance: {str(e)}"

def fund_wallet_in_apt_sync(amount: int, target_address=None):
    """Fund a wallet with APT, defaults to user's or agent's wallet."""
    try:
        if amount is None:
            return "Error: Please specify an amount of APT to fund (maximum 1000 APT)"
        wallet_to_fund = target_address if target_address else get_user_wallet() or str(wallet.address())
        return loop.run_until_complete(fund_wallet(wallet_to_fund, amount))
    except Exception as e:
        return f"Error funding wallet: {str(e)}"

def transfer_in_octa_sync(receiver, amount: int, sender=None):
    """Transfer APT, defaults to sending from agent's wallet."""
    try:
        sender_account = sender if sender else wallet
        return loop.run_until_complete(transfer(sender_account, receiver, amount))
    except Exception as e:
        return f"Error transferring funds: {str(e)}"

def create_token_sync(sender, name: str, symbol: str, icon_uri: str,
                      project_uri: str):
    try:
        return loop.run_until_complete(
            create_token(wallet, name, symbol, icon_uri, project_uri))
    except Exception as e:
        return f"Error creating token: {str(e)}"

def get_transaction_sync(txn_hash: str):
    """Synchronous wrapper for getting transaction details."""
    try:
        return loop.run_until_complete(get_transaction(txn_hash))
    except Exception as e:
        return f"Error getting transaction: {str(e)}"

# TODO: modify this function to truncate massive resource JSON return value from accounts with lots of resources
def get_account_resources_sync(address=None):
    """Get resources for an address or default to agent's address."""
    try:
        target_address = address if address else str(wallet.address())
        print(f"target_address: {target_address}")
        return loop.run_until_complete(get_account_resources(target_address))
    except Exception as e:
        return f"Error getting account resources: {str(e)}"

# Global dictionary to store ABI results for each wallet
ABI_CACHE = {}

# TODO: double check this works well with accounts with various amounts of modules
def get_account_modules_sync(address=None, limit: int = 10):
    """Get modules for an address or default to agent's address, with optional limit."""
    try:
        target_address = address if address else str(wallet.address())
        print(f"target_address: {target_address}")
        abi_result = loop.run_until_complete(get_account_modules(target_address, limit))
        # print(abi_result)
        # ✅ Store the ABI result in cache
        ABI_CACHE[target_address] = abi_result.get("modules", [])

        return abi_result
    except Exception as e:
        return f"Error getting account modules: {str(e)}"

def get_token_balance_sync(address: str, creator_address: str, collection_name: str, token_name: str):
    """Synchronous wrapper for getting token balance."""
    try:
        return loop.run_until_complete(
            get_token_balance(address, creator_address, collection_name, token_name))
    except Exception as e:
        return f"Error getting token balance: {str(e)}"

def execute_view_function_sync(function_id: str, type_args: List[str], args: List[str]) -> dict:
    """
    Synchronous wrapper for executing a Move view function.
    Automatically handles empty arguments and provides detailed error feedback.
    Args:
        function_id: The full function ID (e.g., '0x1::coin::balance').
        type_args: List of type arguments for the function.
        args: List of arguments to pass to the function.
    Returns:
        dict: The result of the view function execution.
    """
    try:
        # Ensure type_args and args are lists (empty if not provided)
        type_args = type_args or []
        args = args or []

        # Debugging: Show what’s being sent
        print(f"Executing view function: {function_id}")
        print(f"Type arguments: {type_args}")
        print(f"Arguments: {args}")

        # Call the async function and return the result
        result = loop.run_until_complete(execute_view_function(function_id, type_args, args))
        return result
    except Exception as e:
        # Improved error message
        return {"error": f"Error executing view function: {str(e)}"}

# New function to execute entry functions
def execute_entry_function_sync(function_id: str, type_args: List[str], args: List[str]) -> dict:
    """
    Executes a Move entry function synchronously, using cached ABI when possible.

    Args:
        function_id: The full function ID (e.g., '0x1::coin::transfer').
        type_args: A list of type arguments for the function (if any).
        args: A list of arguments to pass to the function.

    Returns:
        dict: The transaction hash if successful, otherwise an error message.
    """
    try:
        # ✅ Retrieve ABI from cache if available
        module_address, _ = function_id.split("::", 1) # module address
        abi_cache = ABI_CACHE.get(module_address, [])

        # ✅ Pass cached ABI to avoid unnecessary API calls
        result = loop.run_until_complete(
            execute_entry_function(wallet, function_id, type_args, args, abi_cache=abi_cache, optional_fetch_abi=False)
        )
        return result
    except Exception as e:
        return {"error": f"Error executing entry function: {str(e)}"}

def close_event_loop():
    loop.close()

# Initialize the agent with Gemini (instead of OpenAI) and Crew AI (instead of Swarm)
aptos_agent = Agent(
    name="Aptos Agent",
    model="gemini-1.5-flash",  # Replace with actual Gemini model name
    api_key=os.getenv('GEMINI_API_KEY'),  # Replace with Gemini API key
    role="Blockchain Assistant",  # Add required role
    goal="Help users interact with the Aptos blockchain",  # Add required goal
    backstory="You are an AI agent designed to assist users in executing transactions, querying blockchain data, and deploying smart contracts on Aptos.",  # Add required backstory
    instructions=(  # Keep your existing instructions
        f"You are a helpful agent that can interact on-chain on the Aptos Layer 1 blockchain using the Aptos Python SDK. The dev may speak to you in first person..."
    ),
    functions=[
        fund_wallet_in_apt_sync, get_balance_in_apt_sync,
        transfer_in_octa_sync, create_token_sync,
        get_transaction_sync, get_account_resources_sync,
        get_token_balance_sync, get_account_modules_sync,
        execute_view_function_sync, execute_entry_function_sync, get_user_wallet
    ],
)
