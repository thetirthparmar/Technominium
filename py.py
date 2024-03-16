import bitcoin
import requests
import threading
import colorama
from colorama import Fore, Style
from tabulate import tabulate
import time

colorama.init()

def get_bitcoin_price():
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json")
    data = response.json()
    return data["bpi"]["USD"]["rate_float"]

ascii_art = """                       _          _               _            
  ___ _ __ _   _ _ __ | |_ ___   | |__  _   _ ___| |_ ___ _ __ 
 / __| '__| | | | '_ \| __/ _ \  | '_ \| | | / __| __/ _ \ '__|
| (__| |  | |_| | |_) | || (_) | | |_) | |_| \__ \ ||  __/ |   
 \___|_|   \__, | .__/ \__\___/  |_.__/ \__,_|___/\__\___|_|   
           |___/|_|                                            """

print(Fore.RED + ascii_art + Style.RESET_ALL)

print(Fore.BLUE + "Press Enter To Start Busting" + Style.RESET_ALL)
input()

print(Fore.BLUE + "Do you want to save logs ? y/n" + Style.RESET_ALL)
save_logs_input = input().lower()

if save_logs_input == 'y':
    save_logs = True
elif save_logs_input == 'n':
    save_logs = False
else:
    print(Fore.RED + "Invalid input! Logs will not be saved." + Style.RESET_ALL)
    save_logs = False

print(Fore.BLUE + "Let Me Cook", end="", flush=True)
for _ in range(3):
    print(".", end="", flush=True)
    time.sleep(1)
print("...." + Style.RESET_ALL)

wallet_info = []
total_scanned_wallets = 0
total_busted_wallets = 0
total_balance_hunted = 0
total_busted_amount_usd = 0

def generate_wallet_info():
    global total_scanned_wallets, total_busted_wallets, total_balance_hunted, total_busted_amount_usd
    while True:
        private_key = bitcoin.random_key()
        public_key = bitcoin.privtopub(private_key)
        wallet_address = bitcoin.pubtoaddr(public_key)

        response = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{wallet_address}/balance")
        try:
            balance = response.json()['final_balance']
        except KeyError:
            balance = 0

        wallet_status = "Positive" if balance > 0 else "Negative"

        current_time = time.strftime("%H:%M:%S", time.localtime())

        wallet_info.append([current_time, wallet_address, private_key, balance, wallet_status])

        total_scanned_wallets += 1
        if balance > 0:
            total_busted_wallets += 1
            total_balance_hunted += balance

            bitcoin_price = get_bitcoin_price()
            balance_usd = balance * bitcoin_price
            total_busted_amount_usd += balance_usd

            with open("hunted.txt", "a") as file:
                file.write("Time: {}\n".format(current_time))
                file.write("Wallet Address: {}\n".format(wallet_address))
                file.write("Private Key: {}\n".format(private_key))
                file.write("Balance: {} BTC\n".format(balance))
                file.write("Status: {}\n".format(wallet_status))
                file.write("-" * 30 + "\n")

threads = []
for _ in range(10):
    thread = threading.Thread(target=generate_wallet_info)
    thread.daemon = True
    thread.start()
    threads.append(thread)

while True:
    time.sleep(5)
    print(tabulate(wallet_info, headers=["Time", "Wallet Address", "Private Key", "Balance", "Status"], tablefmt="pretty"))

    if save_logs:
        with open("logs.txt", "w") as file:
            file.write(tabulate(wallet_info, headers=["Time", "Wallet Address", "Private Key", "Balance", "Status"], tablefmt="pretty"))

    print(f"Total Scanned Wallets: {total_scanned_wallets}")
    print(f"Total Busted Wallets: {total_busted_wallets}")
    print(f"Total Balance Hunted: {total_balance_hunted} BTC")
    print(f"Total Busted Amount (USD): {total_busted_amount_usd:.2f} $")
