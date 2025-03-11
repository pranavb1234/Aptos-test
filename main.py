import os
from dotenv import load_dotenv, set_key
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import Field
from aptos_sdk.account import Account
import asyncio
from crewai.tools import BaseTool

# Define a custom tool for interacting with the Aptos blockchain
class AptosBalanceTool(BaseTool):
    name: str = Field(default="aptos_balance_tool")
    description: str = Field(default="Fetches the balance of a given Aptos wallet address.")

    def _run(self, wallet_address: str) -> str:
        """Fetches the balance of a given Aptos wallet address."""
        # Placeholder for actual Aptos SDK interaction to get balance
        # Replace this with actual code to fetch balance
        balance = "1000 APT"  # Example balance
        return f"The balance for wallet {wallet_address} is {balance}."

def check_and_update_env():
    # Load existing environment variables
    load_dotenv()

    # Check for Gemini API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = input("Enter your Gemini API key: ").strip()
        set_key('.env', 'GOOGLE_API_KEY', api_key)
    else:
        print(f"Found Gemini API key: {api_key[:5]}...{api_key[-5:]}")

    # Check for Devnet wallet address
    wallet_address = os.getenv('DEVNET_WALLET_ADDRESS')
    if not wallet_address:
        wallet_address = input("Enter your Devnet wallet address (Optional - Press enter to automatically generate one): ").strip()
        if not wallet_address:
            wallet_address = str(Account.generate().account_address)
            print("Generated user wallet:", wallet_address)
        set_key('.env', 'DEVNET_WALLET_ADDRESS', wallet_address)
    else:
        print(f"Found Devnet wallet address: {wallet_address}")

async def run_crewai_demo():
    load_dotenv()

    # Configure the LLM with the provider and model
    my_llm = LLM(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini/gemini-1.5-flash",
    )

    # Initialize your agents
    financial_agent = Agent(
        role='Financial Analyst',
        goal='Analyze Aptos financial data.',
        backstory="You are an expert financial analyst specializing in Aptos blockchain data.",
        llm=my_llm,
        verbose=True
    )

    aptos_interaction_agent = Agent(
        role='Aptos Interaction Agent',
        goal='Interact with the Aptos blockchain to get information.',
        backstory="You are a specialist in Aptos blockchain interactions.",
        llm=my_llm,
        tools=[AptosBalanceTool()],
        verbose=True
    )

    # Define your tasks
    wallet_address = os.getenv('DEVNET_WALLET_ADDRESS')

    task1 = Task(
        description=f"Get the current balance of Aptos wallet address: {wallet_address}",
        agent=aptos_interaction_agent,
        expected_output="The balance of the wallet address."
    )

    task2 = Task(
        description="Analyze the balance and provide a summary.",
        agent=financial_agent,
        expected_output="A financial analysis summary based on the wallet balance."
    )

    # Create your crew
    crew = Crew(
        agents=[aptos_interaction_agent, financial_agent],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential  # Tasks are executed in sequence
    )

    # Kick off the crew
    result = await crew.kickoff()
    print("\nCrewAI Result:")
    print(result)

if __name__ == "__main__":
    try:
        check_and_update_env()
        asyncio.run(run_crewai_demo())
    except Exception as e:
        print(f"An error occurred: {e}")
