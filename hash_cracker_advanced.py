#!/usr/bin/env python3
import hashlib
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Определение алгоритма по длине хеша
def detect_algorithm(hash_string):
    length = len(hash_string)
    if length == 32:
        return "md5"
    elif length == 40:
        return "sha1"
    elif length == 64:
        return "sha256"
    elif length == 128:
        return "sha512"
    else:
        return None

# Хеширование пароля с поддержкой соли
def hash_password(password, salt, algorithm):
    password_bytes = password.encode('utf-8')
    
    if salt:
        password_bytes = password_bytes + salt.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(password_bytes).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(password_bytes).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(password_bytes).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(password_bytes).hexdigest()
    else:
        return None

# Проверка одного пароля
def check_password(password, target_hash, salt, algorithm):
    password = password.strip()
    hashed = hash_password(password, salt, algorithm)
    if hashed == target_hash:
        return password
    return None

# Прогресс-бар
def progress_bar(current, total, start_time):
    percent = current / total * 100
    bar_length = 30
    filled = int(bar_length * current // total)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    elapsed = time.time() - start_time
    if current > 0:
        eta = (elapsed / current) * (total - current)
        eta_str = f"{eta:.0f}s"
    else:
        eta_str = "?"
    
    sys.stdout.write(f"\r[{bar}] {percent:.1f}% | {current}/{total} | ETA: {eta_str}")
    sys.stdout.flush()

# Основная функция взлома
def crack_hash(target_hash, wordlist_file, salt="", threads=20):
    print(f"{Colors.BLUE}[*] Target hash: {target_hash}{Colors.RESET}")
    
    # Автоопределение алгоритма
    algorithm = detect_algorithm(target_hash)
    if algorithm:
        print(f"{Colors.BLUE}[*] Detected algorithm: {algorithm}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[!] Unknown hash length, please specify algorithm{Colors.RESET}")
        return None
    
    if salt:
        print(f"{Colors.BLUE}[*] Salt: {salt}{Colors.RESET}")
    
    print(f"[*] Wordlist: {wordlist_file}")
    print(f"[*] Threads: {threads}")
    
    # Загрузка словаря
    try:
        with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Colors.RED}[!] Wordlist not found: {wordlist_file}{Colors.RESET}")
        return None
    
    print(f"[*] Loaded {len(passwords)} passwords")
    print(f"[*] Cracking...\n")
    
    start_time = time.time()
    found = None
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_password, pwd, target_hash, salt, algorithm): pwd for pwd in passwords}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            progress_bar(completed, len(passwords), start_time)
            
            result = future.result()
            if result:
                print(f"\n\n{Colors.GREEN}[+] FOUND! Password: {result}{Colors.RESET}")
                print(f"{Colors.GREEN}[+] Time: {time.time() - start_time:.2f} seconds{Colors.RESET}")
                found = result
                break
    
    if not found:
        print(f"\n\n{Colors.RED}[-] Password not found in wordlist{Colors.RESET}")
        print(f"[-] Time: {time.time() - start_time:.2f} seconds")
    
    return found

# Сохранение результатов
def save_result(target_hash, password, salt, algorithm, wordlist, time_taken):
    filename = f"cracked_{int(time.time())}.txt"
    with open(filename, 'w') as f:
        f.write(f"Hash: {target_hash}\n")
        f.write(f"Password: {password}\n")
        f.write(f"Salt: {salt if salt else 'None'}\n")
        f.write(f"Algorithm: {algorithm}\n")
        f.write(f"Wordlist: {wordlist}\n")
        f.write(f"Time: {time_taken:.2f} seconds\n")
    print(f"{Colors.GREEN}[+] Results saved to {filename}{Colors.RESET}")

# CLI
if __name__ == "__main__":
    print("=" * 60)
    print(f"{Colors.YELLOW}🔥 Advanced Hash Cracker - Professional Tool{Colors.RESET}")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python3 hash_cracker_advanced.py <hash> <wordlist> [salt] [threads]")
        print("\nExamples:")
        print("  python3 hash_cracker_advanced.py 5f4dcc3b5aa765d61d8327deb882cf99 passwords.txt")
        print("  python3 hash_cracker_advanced.py 5f4dcc3b5aa765d61d8327deb882cf99 passwords.txt \"\" 30")
        print("  python3 hash_cracker_advanced.py 8d6a3f6f7c8f4b6a9e8f6d4a3b2c1e0f passwords.txt \"salt123\"")
        print("\nSupported hash lengths:")
        print("  32 chars → MD5")
        print("  40 chars → SHA1")
        print("  64 chars → SHA256")
        print("  128 chars → SHA512")
        print("=" * 60)
        sys.exit(1)
    
    target_hash = sys.argv[1]
    wordlist = sys.argv[2]
    salt = sys.argv[3] if len(sys.argv) > 3 else ""
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    
    result = crack_hash(target_hash, wordlist, salt, threads)
    
    if result:
        algorithm = detect_algorithm(target_hash)
        save_result(target_hash, result, salt, algorithm, wordlist, 0)
