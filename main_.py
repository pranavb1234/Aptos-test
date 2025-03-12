import os
import asyncio
import requests
from dotenv import load_dotenv, set_key
from aptos_sdk.account import Account
from aptos_sdk.client import RestClient
from aptos_sdk.transactions import TransactionPayload
from aptos_sdk.bcs import Serializer
from aptos_sdk.authenticator import Authenticator
from aptos_sdk.transaction_builder import TransactionBuilder
from aptos_sdk.chain_ids import TESTNET
from agents import close_event_loop, aptos_agent
from swarm.repl import run_demo_loop

# Load environment variables
def check_and_update_env():
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        gemini_key = input("Enter your Gemini API key: ").strip()
        set_key(".env", "GEMINI_API_KEY", gemini_key)
    else:
        print(f"Found Gemini API key: {gemini_key[:5]}...{gemini_key[-5:]}")

    # Aptos Wallet
    wallet_private_key = os.getenv("DEVNET_WALLET_PRIVATE_KEY")
    if not wallet_private_key:
        account = Account.generate()
        wallet_private_key = account.private_key.hex()
        set_key(".env", "DEVNET_WALLET_PRIVATE_KEY", wallet_private_key)
        print(f"Generated new wallet: {account.account_address}")
    else:
        print("Using existing wallet.")

class AptosTransactionHandler:
    def __init__(self):
        self.client = RestClient("https://fullnode.devnet.aptoslabs.com")
        self.account = Account.load_key(bytes.fromhex(os.getenv("DEVNET_WALLET_PRIVATE_KEY")))

    def get_balance(self):
        return self.client.account_balance(self.account.account_address)

    def execute_transaction(self, module_name, function_name, args):
        """Executes a Move smart contract transaction."""
        payload = TransactionPayload.entry_function(
            module=module_name,
            function=function_name,
            ty_args=[],
            args=[Serializer.str(arg).output() for arg in args],
        )

        txn = TransactionBuilder(
            sender=self.account.account_address,
            sequence_number=self.client.account_sequence_number(self.account.account_address),
            payload=payload,
            gas_unit_price=100,
            max_gas_amount=1000,
            expiration_timestamp_secs=60,
            chain_id=TESTNET,
            authenticator=Authenticator.ed25519(self.account.private_key),
        ).sign(self.account)

        txn_hash = self.client.submit_bcs_transaction(txn)
        self.client.wait_for_transaction(txn_hash)
        new_balance = self.get_balance()

        return txn_hash, new_balance

def query_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": os.getenv("GEMINI_API_KEY")}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(url, headers=headers, params=params, json=data)
    return response.json()

if __name__ == "__main__":
    try:
        check_and_update_env()
        handler = AptosTransactionHandler()

      
        response = query_gemini("What crypto should I invest in?")
        print("Gemini AI Suggestion:", response)

   
        txn_hash, balance = handler.execute_transaction("main", "transfer", ["0xReceiverAddress", "1000000"])
        print(f"Transaction Hash: {txn_hash}")
        print(f"Updated Balance: {balance} APT")

        # Run interactive REPL
        asyncio.run(run_demo_loop(aptos_agent, stream=True))
    
    finally:
        close_event_loop()
