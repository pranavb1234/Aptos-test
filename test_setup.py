import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_connection():
    """Test Gemini API connection"""
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')  # or 'gemini-pro-vision' for images
        response = model.generate_content("Say hello!")
        print("Gemini Connection Test:", response.text)
        return True
    except Exception as e:
        print(f"Gemini Connection Error: {str(e)}")
        return False

def test_aptos_connection():
    """Test Aptos connection"""
    from agents import get_balance_in_apt_sync
    try:
        balance = get_balance_in_apt_sync()
        print(f"Aptos Connection Test - Balance: {balance}")
        return True
    except Exception as e:
        print(f"Aptos Connection Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing connections...")
    gemini_ok = test_gemini_connection()
    aptos_ok = test_aptos_connection()

    if gemini_ok and aptos_ok:
        print("\n✅ All connections successful!")
    else:
        print("\n❌ Some connections failed. Check errors above.")