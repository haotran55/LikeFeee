import requests
import json
import os
import re
from pathlib import Path

def display_ascii_art():
    print(r"""
 █████╗ ██╗  ██╗██╗    ██████╗  ██╗   ██╗
██╔══██╗██║ ██╔╝██║    ██╔══██╗ ██║   ██║
███████║█████╔╝ ██║    ██████╔╝ ██║   ██║
██╔══██║██╔═██╗ ██║    ██╔══██╗ ██║   ██║
██║  ██║██║  ██╗██║    ██║  ██║ ╚██████╔╝
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝    ╚═╝  ╚═╝  ╚═════╝ 
""")

def fetch_token(uid, password):
    url = f"https://ariflexlabs-jwt-gen.onrender.com/fetch-token?uid={uid}&password={password}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('JWT TOKEN')
        else:
            print(f"❌ Error fetching token for UID {uid}: HTTP {response.status_code}")
            return None
    except requests.Timeout:
        print(f"⌛ Timeout occurred while fetching token for UID {uid}")
        return None
    except Exception as e:
        print(f"⚠️ Exception occurred: {str(e)}")
        return None

def process_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            accounts = json.load(file)
        
        tokens = []
        for idx, account in enumerate(accounts, 1):
            uid = account.get('uid')
            password = account.get('password')
            if uid and password:
                print(f"\n🔹 Processing account {idx}/{len(accounts)} - UID: {uid}")
                token = fetch_token(uid, password)
                if token:
                    tokens.append({"token": token})
                    print("✅ Token generated successfully!")
                else:
                    print("❌ Failed to generate token")
            else:
                print(f"⚠️ Skipping invalid account (missing uid or password)")
        
        return tokens
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON file format")
        return []
    except Exception as e:
        print(f"⚠️ Error processing file: {str(e)}")
        return []

def process_guest_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        guest_info = data.get('guest_account_info', {})
        uid = guest_info.get('com.garena.msdk.guest_uid')
        password = guest_info.get('com.garena.msdk.guest_password')
        
        if uid and password:
            print(f"\n🔹 Processing Guest UID: {uid}")
            token = fetch_token(uid, password)
            if token:
                print("✅ Token generated successfully!")
                return [{"token": token}]
            else:
                print("❌ Failed to generate token")
                return []
        else:
            print("⚠️ Invalid guest file format (missing uid or password)")
            return []
    except json.JSONDecodeError:
        print("❌ Error: Invalid guest file format")
        return []
    except Exception as e:
        print(f"⚠️ Error processing file: {str(e)}")
        return []

def process_guest_files(directory):
    try:
        guest_files = [f for f in os.listdir(directory) if re.match(r'guest\d+\.dat', f)]
        if not guest_files:
            print("❌ No guest files found in the directory")
            return []
        
        print(f"\nFound {len(guest_files)} guest files to process...")
        tokens = []
        
        for idx, guest_file in enumerate(guest_files, 1):
            print(f"\n📁 Processing file {idx}/{len(guest_files)}: {guest_file}")
            file_tokens = process_guest_file(os.path.join(directory, guest_file))
            if file_tokens:
                tokens.extend(file_tokens)
        
        return tokens
    except Exception as e:
        print(f"⚠️ Error reading directory: {str(e)}")
        return []

def save_tokens(tokens, output_file='AKIRU-JWT.json'):
    try:
        with open(output_file, 'w') as file:
            json.dump(tokens, file, indent=4)
        print(f"\n💾 Successfully saved {len(tokens)} tokens to '{output_file}'")
        print(f"📂 File location: {os.path.abspath(output_file)}")
    except Exception as e:
        print(f"❌ Error saving tokens: {str(e)}")

def get_file_path(prompt, default):
    while True:
        path = input(prompt).strip()
        path = path if path else default
        if os.path.exists(path):
            return path
        print(f"❌ Path does not exist: {path}\nPlease try again.")

def main():
    display_ascii_art()
    
    while True:
        print("\n" + "="*40)
        print("MAIN MENU".center(40))
        print("="*40)
        print("1. Process from JSON file (multiple accounts)")
        print("2. Process from guest files (guest*.dat)")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ").strip()
        
        if choice == '1':
            print("\n" + " JSON File Processing ".center(40, "-"))
            file_path = get_file_path(
                "Enter JSON file path [default: accounts.json]: ",
                "accounts.json"
            )
            tokens = process_json_file(file_path)
            if tokens:
                save_tokens(tokens)
        
        elif choice == '2':
            print("\n" + " Guest Files Processing ".center(40, "-"))
            dir_path = get_file_path(
                "Enter directory path [default: current directory]: ",
                "."
            )
            tokens = process_guest_files(dir_path)
            if tokens:
                save_tokens(tokens)
        
        elif choice == '3':
            print("\n👋 Thank you for using the JWT Generator!")
            break
        
        else:
            print("❌ Invalid option. Please select 1, 2, or 3.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()