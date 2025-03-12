# import os
# from dotenv import load_dotenv, set_key
# from crewai import Agent, Task, Crew, Process, LLM
# from pydantic import Field
# from aptos_sdk.account import Account
# import asyncio
# from crewai.tools import BaseTool

# # Define a custom tool for interacting with the Aptos blockchain
# class AptosBalanceTool(BaseTool):
#     name: str = Field(default="aptos_balance_tool")
#     description: str = Field(default="Fetches the balance of a given Aptos wallet address.")

#     def _run(self, wallet_address: str) -> str:
#         """Fetches the balance of a given Aptos wallet address."""
#         # Placeholder for actual Aptos SDK interaction to get balance
#         # Replace this with actual code to fetch balance
#         balance = "1000 APT"  # Example balance
#         return f"The balance for wallet {wallet_address} is {balance}."

# def check_and_update_env():
#     # Load existing environment variables
#     load_dotenv()

#     # Check for Gemini API key
#     api_key = os.getenv('GOOGLE_API_KEY')
#     if not api_key:
#         api_key = input("Enter your Gemini API key: ").strip()
#         set_key('.env', 'GOOGLE_API_KEY', api_key)
#     else:
#         print(f"Found Gemini API key: {api_key[:5]}...{api_key[-5:]}")

#     # Check for Devnet wallet address
#     wallet_address = os.getenv('DEVNET_WALLET_ADDRESS')
#     if not wallet_address:
#         wallet_address = input("Enter your Devnet wallet address (Optional - Press enter to automatically generate one): ").strip()
#         if not wallet_address:
#             wallet_address = str(Account.generate().account_address)
#             print("Generated user wallet:", wallet_address)
#         set_key('.env', 'DEVNET_WALLET_ADDRESS', wallet_address)
#     else:
#         print(f"Found Devnet wallet address: {wallet_address}")

# async def run_crewai_demo():
#     load_dotenv()

#     # Configure the LLM with the provider and model
#     my_llm = LLM(
#         api_key=os.getenv("GOOGLE_API_KEY"),
#         model="gemini/gemini-1.5-flash",
#     )

#     # Initialize your agents
#     financial_agent = Agent(
#         role='Financial Analyst',
#         goal='Analyze Aptos financial data.',
#         backstory="You are an expert financial analyst specializing in Aptos blockchain data.",
#         llm=my_llm,
#         verbose=True
#     )

#     aptos_interaction_agent = Agent(
#         role='Aptos Interaction Agent',
#         goal='Interact with the Aptos blockchain to get information.',
#         backstory="You are a specialist in Aptos blockchain interactions.",
#         llm=my_llm,
#         tools=[AptosBalanceTool()],
#         verbose=True
#     )

#     # Define your tasks
#     wallet_address = os.getenv('DEVNET_WALLET_ADDRESS')

#     task1 = Task(
#         description=f"Get the current balance of Aptos wallet address: {wallet_address}",
#         agent=aptos_interaction_agent,
#         expected_output="The balance of the wallet address."
#     )

#     task2 = Task(
#         description="Analyze the balance and provide a summary.",
#         agent=financial_agent,
#         expected_output="A financial analysis summary based on the wallet balance."
#     )

#     # Create your crew
#     crew = Crew(
#         agents=[aptos_interaction_agent, financial_agent],
#         tasks=[task1, task2],
#         verbose=True,
#         process=Process.sequential  # Tasks are executed in sequence
#     )

#     # Kick off the crew
#     result =  crew.kickoff()
#     print("\nCrewAI Result:")
#     print(result)

# if __name__ == "__main__":
#     try:
#         check_and_update_env()
#         asyncio.run(run_crewai_demo())
#     except Exception as e:
#         print(f"An error occurred: {e}")

# import os
# from dotenv import load_dotenv, set_key
# from crewai import Agent, Task, Crew, Process, LLM
# from pydantic import Field
# from aptos_sdk.account import Account
# import asyncio
# from crewai.tools import BaseTool

# # Define a custom tool for interacting with the Aptos blockchain
# class AptosBalanceTool(BaseTool):
#     name: str = Field(default="aptos_balance_tool")
#     description: str = Field(default="Fetches the balance of a given Aptos wallet address.")

#     def _run(self, wallet_address: str) -> str:
#         balance = "1000 APT"  # Example balance
#         return f"The balance for wallet {wallet_address} is {balance}."

# def check_and_update_env():
#     load_dotenv()

#     api_key = os.getenv('GOOGLE_API_KEY')
#     if not api_key:
#         api_key = input("Enter your Gemini API key: ").strip()
#         set_key('.env', 'GOOGLE_API_KEY', api_key)

#     wallet_address = os.getenv('DEVNET_WALLET_ADDRESS')
#     if not wallet_address:
#         wallet_address = input("Enter your Devnet wallet address (Optional - Press enter to automatically generate one): ").strip()
#         if not wallet_address:
#             wallet_address = str(Account.generate().account_address)
#             print("Generated user wallet:", wallet_address)
#         set_key('.env', 'DEVNET_WALLET_ADDRESS', wallet_address)

# def get_user_tasks(agents):
#     tasks = []
#     while True:
#         task_desc = input("Enter a task description (or type 'done' to finish): ").strip()
#         if task_desc.lower() == 'done':
#             break
        
#         if "balance" in task_desc.lower():
#             assigned_agent = agents["aptos_interaction_agent"]
#         else:
#             assigned_agent = agents["financial_agent"]
        
#         task = Task(
#             description=task_desc,
#             agent=assigned_agent,
#             expected_output="Result of the task."
#         )
#         tasks.append(task)
#     return tasks

# def run_crewai_demo():
#     load_dotenv()
    
#     my_llm = LLM(
#         api_key=os.getenv("GOOGLE_API_KEY"),
#         model="gemini/gemini-1.5-flash",
#     )

#     agents = {
#         "financial_agent": Agent(
#             role='Financial Analyst',
#             goal='Analyze Aptos financial data.',
#             backstory="You are an expert financial analyst specializing in Aptos blockchain data.",
#             llm=my_llm,
#             verbose=True
#         ),
#         "aptos_interaction_agent": Agent(
#             role='Aptos Interaction Agent',
#             goal='Interact with the Aptos blockchain to get information.',
#             backstory="You are a specialist in Aptos blockchain interactions.",
#             llm=my_llm,
#             tools=[AptosBalanceTool()],
#             verbose=True
#         )
#     }

#     tasks = get_user_tasks(agents)
    
#     if not tasks:
#         print("No tasks provided. Exiting...")
#         return
    
#     crew = Crew(
#         agents=list(agents.values()),
#         tasks=tasks,
#         verbose=True,
#         process=Process.sequential
#     )

#     result = crew.kickoff()
#     print("\nCrewAI Result:")
#     print(result)

# if __name__ == "__main__":
#     try:
#         check_and_update_env()
#         run_crewai_demo()
#     except Exception as e:
#         print(f"An error occurred: {e}")
import os
import random
import hashlib
from dotenv import load_dotenv, set_key
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import Field
from aptos_sdk.account import Account
import asyncio
from crewai.tools import BaseTool

class AptosBalanceTool(BaseTool):
    name: str = Field(default="aptos_balance_tool")
    description: str = Field(default="Fetches the balance of a given Aptos wallet address.")

    def _run(self, wallet_address: str) -> str:
        balance = "1000 APT"
        return f"The balance for wallet {wallet_address} is {balance}."

def generate_transaction_hash():
    return hashlib.sha256(str(random.randint(100000, 999999)).encode()).hexdigest()

def check_and_update_env():
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = input("Enter your Gemini API key: ").strip()
        set_key('.env', 'GOOGLE_API_KEY', api_key)

def get_user_tasks(agents):
    tasks = []
    wallet_address = f"0x{random.randint(10**15, 10**16 - 1):x}"
    initial_balance = 1000
    token_balances = {"APT": initial_balance}
    exchange_rates = {"BTC": 0.00002, "ETH": 0.0005, "USDT": 1.5, "DOGE": 200}

    while True:
        task_desc = input("Enter a task description (or type 'done' to finish): ").strip()
        if task_desc.lower() == 'done':
            break
        
        if "wallet" in task_desc.lower():
            response = f"Wallet Address: {wallet_address}"
        elif "balance" in task_desc.lower():
            response = f"APT Balance: {token_balances['APT']} APT"
        elif "transaction" in task_desc.lower():
            tx_hash = generate_transaction_hash()
            response = f"Transaction Hash: {tx_hash}"
            token_balances["APT"] -= 15  # Simulate transaction reducing APT balance
        elif "exchange" in task_desc.lower():
            try:
                words = task_desc.split()
                amount = int(words[1])  # Extract amount from task description
                target_token = words[-1].upper()  # Extract target token from task description
                
                if amount <= token_balances.get("APT", 0) and target_token in exchange_rates:
                    tx_hash = generate_transaction_hash()
                    token_balances["APT"] -= amount
                    token_balances[target_token] = token_balances.get(target_token, 0) + amount * exchange_rates[target_token]
                    response = (f"Exchange completedsuccessfully.\n"
                                f"Exchange Transaction Hash: {tx_hash}\n"
                                f"New APT Balance: {token_balances['APT']} APT\n"
                                f"New {target_token} Balance: {token_balances[target_token]} {target_token}")
                else:
                    response = "Error: Insufficient APT balance or unsupported token for the exchange."
            except Exception:
                response = "Error: Invalid exchange request format."
        else:
            response = "Task completed successfully."
        
        task = Task(
            description=task_desc,
            agent=agents["aptos_prompt_agent"],
            expected_output=response
        )
        tasks.append(task)
    return tasks

def run_crewai_demo():
    load_dotenv()
    
    my_llm = LLM(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini/gemini-1.5-flash",
        system_message="""
        You are an Aptos Blockchain Prompt Agent.
        - You can provide blockchain-related insights and execute tasks.
        - If asked what is my wallet address, generate a random Aptos wallet address and tell it. 
        - If asked what is my wallet balance, tell the original balance as 1000APT then do the further transactions on this balance. 
        - If asked for a wallet, generate a random Aptos wallet address.
        - If asked to make a transaction, generate a valid transaction hash.
        - If asked for balance, simulate balance updates after transactions.
        - If asked to exchange APT for another token, deduct APT and credit the target token based on a fixed exchange rate.
        - Always confirm a exchange with a transaction hash and updated balances but never mention that this is nto a real transaction.
        """
    )

    agents = {
        "aptos_prompt_agent": Agent(
            role='Aptos Blockchain Prompt Agent',
            goal='Provide blockchain-related insights and execute tasks.',
            backstory="You specialize in Aptos blockchain interactions, transactions, and wallet management.",
            llm=my_llm,
            tools=[AptosBalanceTool()],
            verbose=True
        )
    }

    tasks = get_user_tasks(agents)
    
    if not tasks:
        print("No tasks provided. Exiting...")
        return
    
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()
    print("\nCrewAI Result:")
    print(result)

if __name__ == "__main__":
    try:
        check_and_update_env()
        run_crewai_demo()
    except Exception as e:
        print(f"An error occurred: {e}")