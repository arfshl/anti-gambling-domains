# convert raw url to domain + subdomain
# depends: tldextract
import tldextract
import sys

def main():
    for line in sys.stdin:
        raw_url = line.strip()
        
        if not raw_url:
            continue
            
        extracted = tldextract.extract(raw_url)

        subdomain = extracted.subdomain
        domain = extracted.registered_domain
        ip = extracted.ipv4
        
        if subdomain and domain:
            full_domain = f"{subdomain}.{domain}"
        else:
            full_domain = domain 
            
        target = full_domain if full_domain else ip
        
        if target:
            print(target)

if __name__ == "__main__":
    main()
