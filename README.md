
---

<!--# WaybackLister-->

<img width="550" alt="Screenshot 2025-06-27 at 8 04 32 AM" src="https://github.com/user-attachments/assets/10b6c7da-546a-444b-b27a-824299bdab72" />

> **WaybackLister v1.1** — by [FR13ND0x7F]  
> Discover potential directory listings through archived URLs from the Wayback Machine.

---

## 🕵️‍♂️ What It Does

WaybackLister is a reconnaissance tool that taps into the Wayback Machine to fetch historical URLs for a domain, parses unique paths, and checks if any of those paths currently expose **directory listings**. It's fast, multithreaded, and built for practical use in security assessments and bug bounty recon.

---

## 🚀 Features

- Pulls archived URLs via the Wayback Machine
- Extracts unique paths and subdomains from those URLs
- Actively checks for live directory listings
- Supports multithreaded scanning
- Can auto-discover subdomains based on Wayback data
- Works with single domain or list of domains
- Retry logic for timeouts [v1.1] 

---

## 📦 Installation

Clone the repo and you're good to go:

```bash
git clone https://github.com/anmolksachan/wayBackLister.git
cd wayBackLister
pip install -r requirements.txt -> To be updated
```

---

## 🛠 Usage

### Scan a Single Domain

```bash
python waybacklister.py -d example.com
```

### Scan Multiple Domains from a File

```bash
python waybacklister.py -f domains.txt
```

### Auto-discover and Scan Subdomains [Module Under Development]

```bash
python waybacklister.py -auto example.com 
```

### Custom Thread Count

```bash
python waybacklister.py -d example.com -t 20
```

---

## 📄 Example Output

```
[+] Querying Wayback Machine for example.com...
[*] Attempt 1 to fetch data for example.com
[+] Processing domain: example.com
[+] Found 154 unique paths for example.com. Checking for directory listings...
[+] Directory Listing Found: http://example.com/files/
[+] Directory Listing Found: http://example.com/uploads/

[+] Summary of Directory Listings for example.com:
http://example.com/files/
http://example.com/uploads/
```

---

## 📄 Example

<img width="718" alt="Screenshot 2025-06-27 at 8 11 27 AM" src="https://github.com/user-attachments/assets/55e16e8f-3c89-408b-b501-bd2405ee7739" />
<!--v1.0 ![image](https://github.com/user-attachments/assets/62bb5035-94fc-432d-ae14-daa823b2aebe)-->

---

## ⚙️ Requirements

- Python 3.6+
- `requests`
- `argparse`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🧠 Why This Tool?

Sometimes, old URLs archived by the Wayback Machine lead to interesting places—especially when they still work. Directory listings can reveal sensitive files, backups, or even forgotten admin panels. WaybackLister helps you find them in a systematic and scriptable way.

---

## Community Blogs/ Resources
- ([How I Use Waybacklister to Discover Gold in Bug Bounty Targets 💰](https://www.youtube.com/watch?v=N_uROnZ0q58&ab_channel=PCPLALEX))
- ([WayBackLister : Innovative Directory Bruteforcing Technique](https://systemweakness.com/waybacklister-innovative-directory-bruteforcing-technique-43535da40bc4))
- ([Recon Tool: WaybackLister](https://www.blackhatethicalhacking.com/tools/waybacklister/))

---

## 📢 Disclaimer

This tool is meant for educational and authorized security testing only. Don't use it on systems you don't have permission to test.

---

## 🙌 Acknowledgements

Crafted by ([FR13ND0x7F @anmolksachan](https://x.com/fr13nd0x7f)) — for the community, by the community.

---
