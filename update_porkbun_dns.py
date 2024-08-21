import requests

# Configuration
API_KEY = 'Enter your API key here'
API_SECRET = 'Enter your API secret key here'
DOMAIN = 'Enter your domain here'

# API Endpoints
RETRIEVE_URL = f'https://porkbun.com/api/json/v3/dns/retrieve/{DOMAIN}'
UPDATE_URL_TEMPLATE = f'https://porkbun.com/api/json/v3/dns/edit/{DOMAIN}/{{record_id}}'

def get_public_ip():
    response = requests.get('https://api.ipify.org?format=json')
    return response.json()['ip']

def get_dns_records():
    data = {
        'apikey': API_KEY,
        'secretapikey': API_SECRET
    }
    response = requests.post(RETRIEVE_URL, json=data)
    return response.json()

def update_dns_record(record_id, ip_address, name):
    data = {
        'apikey': API_KEY,
        'secretapikey': API_SECRET,
        'type': 'A',
        'name': name,  # Use the same name as the current record
        'content': ip_address,
        'ttl': 300  # Time to live, in seconds
    }
    update_url = UPDATE_URL_TEMPLATE.format(record_id=record_id)
    response = requests.post(update_url, json=data)
    return response.json()

def main():
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
                print(f"Processing A record ID: {record_id}, Name: {record_name}, Current DNS IP: {dns_ip}")
                
                # Step 3: Compare IPs and update if different
                if current_ip != dns_ip:
                    print(f"IP address is different for record {record_name}. Updating DNS record...")
                    update_response = update_dns_record(record_id, current_ip, record_name)
                    print(f"Update Response for {record_name}: {update_response}")
                else:
                    print(f"IP address matches the DNS record for {record_name}. No update needed.")
    else:
        print("No DNS records found or failed to retrieve records. Please check the domain and API key.")

if __name__ == '__main__':
    main()
