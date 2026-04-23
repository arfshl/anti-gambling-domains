# convert raw url to domain only
# depends: tldextract
import tldextract
import sys

def main():
    for line in sys.stdin:
        raw_url = line.strip()
        
        if not raw_url:
            continue
            
        extracted = tldextract.extract(raw_url)
        
        domain = extracted.registered_domain
        ip = extracted.ipv4
        
        target = domain if domain else ip
        
        if target:
            print(target)

if __name__ == "__main__":
    main()
