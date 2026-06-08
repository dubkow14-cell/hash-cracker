#!/usr/bin/env python3
import hashlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor

def hash_password(password, algorithm="md5"):
    """Хеширует пароль указанным алгоритмом"""
    password_bytes = password.encode('utf-8')
    
    if algorithm.lower() == "md5":
        return hashlib.md5(password_bytes).hexdigest()
    elif algorithm.lower() == "sha1":
        return hashlib.sha1(password_bytes).hexdigest()
    elif algorithm.lower() == "sha256":
        return hashlib.sha256(password_bytes).hexdigest()
    else:
        return None

def check_password(password, target_hash, algorithm):
    """Проверяет один пароль"""
    hashed = hash_password(password.strip(), algorithm)
    if hashed == target_hash:
        return password.strip()
    return None

def crack_hash_multithreaded(target_hash, wordlist_file, algorithm="md5", threads=10):
    """Многопоточный перебор паролей"""
    print(f"[*] Target hash: {target_hash}")
    print(f"[*] Algorithm: {algorithm}")
    print(f"[*] Wordlist: {wordlist_file}")
    print(f"[*] Threads: {threads}")
    
    try:
        with open(wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = f.readlines()
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {wordlist_file}")
        return None
    
    print(f"[*] Loaded {len(passwords)} passwords")
    print("[*] Cracking...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_password, pwd, target_hash, algorithm): pwd for pwd in passwords}
        
        for future in futures:
            result = future.result()
            if result:
                elapsed = time.time() - start_time
                print(f"\n[+] FOUND! Password: {result}")
                print(f"[+] Time: {elapsed:.2f} seconds")
                return result
    
    elapsed = time.time() - start_time
    print(f"\n[-] Password not found in wordlist")
    print(f"[-] Time: {elapsed:.2f} seconds")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("=" * 50)
        print("Hash Cracker - Dictionary Attack Tool")
        print("=" * 50)
        print("\nUsage:")
        print("  python3 hash_cracker.py <hash> <wordlist> [algorithm] [threads]")
        print("\nExamples:")
        print("  python3 hash_cracker.py 5f4dcc3b5aa765d61d8327deb882cf99 passwords.txt md5")
        print("  python3 hash_cracker.py 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 passwords.txt sha1 20")
        print("\nTest hashes:")
        print("  MD5 of 'password': 5f4dcc3b5aa765d61d8327deb882cf99")
        print("  SHA1 of 'admin': d033e22ae348aeb5660fc2140aec35850c4da997")
        print("=" * 50)
        sys.exit(1)
    
    target_hash = sys.argv[1]
    wordlist = sys.argv[2]
    algorithm = sys.argv[3] if len(sys.argv) > 3 else "md5"
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    
    crack_hash_multithreaded(target_hash, wordlist, algorithm, threads)
