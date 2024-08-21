import requests

# Configuration
API_KEY = 'Enter your API key here'
API_SECRET = 'Enter your API secret key here'
DOMAIN = ''

# API Endpoints
RETRIEVE_URL = f'https://porkbun.com/api/json/v3/dns/retrieve/{DOMAIN}'
UPDATE_URL_TEMPLATE = f'https://porkbun.com/api/json/v3/dns/edit/{DOMAIN}/{{record_id}}'

def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()  # Raise an error for HTTP issues
    return response.json()['ip']

def get_dns_records():
    data = {
        'apikey': API_KEY,
        'secretapikey': API_SECRET
    }
    response = requests.post(RETRIEVE_URL, json=data)
    response.raise_for_status()  # Raise an error for HTTP issues
    return response.json()

def update_dns_record(record_id, ip_address, name):
    data = {
        'apikey': API_KEY,
        'secretapikey': API_SECRET,
        'type': 'A',
        'name': name,  # Subdomain or root domain
        'content': ip_address,
        'ttl': 300  # Time to live, in seconds
    }
    update_url = UPDATE_URL_TEMPLATE.format(record_id=record_id)
    response = requests.post(update_url, json=data)
    response.raise_for_status()  # Raise an error for HTTP issues
    return response.json()

def strip_domain(record_name, domain):
    """Remove the main domain from the record name to get the subdomain."""
    if record_name.endswith(domain):
        subdomain = record_name[:-len(domain)]
        # Remove the trailing dot if it exists
        if subdomain.endswith('.'):
            subdomain = subdomain[:-1]
        return subdomain
    return record_name

def main():
    try:
        # Step 1: Get current public IP
        current_ip = get_public_ip()
        print(f"Your current IP: {current_ip}")
        
        # Step 2: Retrieve DNS records
        dns_records = get_dns_records()
        
        if 'records' in dns_records:
            print("DNS Records found. Processing...")
            for record in dns_records['records']:
                # Process only A records
                if record['type'] == 'A':
                    record_id = record['id']
                    record_name = record['name']
                    dns_ip = record['content']
                    
                    # Strip domain to get the subdomain
                    subdomain = strip_domain(record_name, DOMAIN)
                    
                    print(f"Processing A record ID: {record_id}, Name: {subdomain}.{DOMAIN}, Current DNS IP: {dns_ip}")
                    
                    # Step 3: Compare IPs and update if different
                    if current_ip != dns_ip:
                        print(f"IP address is different for record {subdomain}.{DOMAIN}. Updating DNS record...")
                        update_response = update_dns_record(record_id, current_ip, subdomain)
                        print(f"Update Response for {subdomain}.{DOMAIN}: {update_response}")
                    else:
                        print(f"IP address matches the DNS record for {subdomain}.{DOMAIN}. No update needed.")
        else:
            print("No DNS records found or failed to retrieve records. Please check the domain and API key.")
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
