import os
from dotenv import load_dotenv, set_key
import google.generativeai as genai
from crewai import Agent, Task, Crew, Process
from agents import close_event_loop, aptos_agent
from aptos_sdk.account import Account
import asyncio

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
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

    # Initialize your agents (replace with your actual agents)
    financial_agent = Agent(
        role='Financial Analyst',
        goal='Analyze Aptos financial data.',
        backstory="You are an expert financial analyst specializing in Aptos blockchain data.",
        llm=genai.GenerativeModel('gemini-1.5-flash'),
        verbose=True
    )

    aptos_interaction_agent = Agent(
        role='Aptos Interaction Agent',
        goal='Interact with the Aptos blockchain to get information.',
        backstory="You are a specialist in Aptos blockchain interactions.",
        llm=genai.GenerativeModel('gemini-1.5-flash'),
        tools=[aptos_agent], #use the aptos agent as a tool.
        verbose=True
    )

    # Define your tasks
    task1 = Task(
        description="Get the current balance of the provided Aptos wallet address.",
        agent=aptos_interaction_agent
    )

    task2 = Task(
        description="Analyze the balance and provide a summary.",
        agent=financial_agent
    )

    # Create your crew
    crew = Crew(
        agents=[aptos_interaction_agent, financial_agent],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential  # Tasks are executed in sequence
    )

    # Kick off the crew
    result = crew.kickoff()
    print("\nCrewAI Result:")
    print(result)

if __name__ == "__main__":
    try:
        check_and_update_env()
        asyncio.run(run_crewai_demo())
    finally:
        close_event_loop()