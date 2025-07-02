"""
Simple offline IP database for common IPs and major ISPs
"""
import ipaddress

# Common IP ranges and their locations
IP_RANGES = {
    # Google
    '8.8.8.8': {'city': 'Mountain View', 'country': 'United States', 'isp': 'Google'},
    '8.8.4.4': {'city': 'Mountain View', 'country': 'United States', 'isp': 'Google'},
    
    # Cloudflare
    '1.1.1.1': {'city': 'Sydney', 'country': 'Australia', 'isp': 'Cloudflare'},
    '1.0.0.1': {'city': 'Sydney', 'country': 'Australia', 'isp': 'Cloudflare'},
    
    # OpenDNS
    '208.67.222.222': {'city': 'San Jose', 'country': 'United States', 'isp': 'OpenDNS'},
    '208.67.220.220': {'city': 'San Jose', 'country': 'United States', 'isp': 'OpenDNS'},
    
    # Quad9
    '9.9.9.9': {'city': 'Zurich', 'country': 'Switzerland', 'isp': 'Quad9'},
    
    # Major Indian ISPs
    '59.94.107.152': {'city': 'Kalpatta', 'country': 'India', 'isp': 'BSNL'},
    '103.21.244.0': {'city': 'Mumbai', 'country': 'India', 'isp': 'Cloudflare'},
    '103.22.200.0': {'city': 'Delhi', 'country': 'India', 'isp': 'BSNL'},
    '103.23.108.0': {'city': 'Chennai', 'country': 'India', 'isp': 'BSNL'},
    '103.24.76.0': {'city': 'Kolkata', 'country': 'India', 'isp': 'BSNL'},
    '103.25.44.0': {'city': 'Bangalore', 'country': 'India', 'isp': 'BSNL'},
    '103.26.12.0': {'city': 'Hyderabad', 'country': 'India', 'isp': 'BSNL'},
    '103.27.180.0': {'city': 'Pune', 'country': 'India', 'isp': 'BSNL'},
    '103.28.148.0': {'city': 'Ahmedabad', 'country': 'India', 'isp': 'BSNL'},
    '103.29.116.0': {'city': 'Jaipur', 'country': 'India', 'isp': 'BSNL'},
}

# Major ISP ranges (simplified)
ISP_RANGES = {
    # BSNL India
    '59.94.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.22.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.23.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.24.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.25.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.26.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.27.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.28.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    '103.29.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'BSNL'},
    
    # Airtel India
    '122.160.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.161.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.162.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.163.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.164.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.165.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.166.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.167.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.168.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.169.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.170.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.171.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.172.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.173.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.174.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.175.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.176.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.177.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.178.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.179.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.180.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.181.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.182.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.183.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.184.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.185.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.186.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.187.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.188.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.189.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.190.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.191.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.192.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.193.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.194.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.195.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.196.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.197.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.198.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.199.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.200.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.201.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.202.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.203.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.204.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.205.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.206.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.207.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.208.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.209.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.210.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.211.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.212.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.213.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.214.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.215.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.216.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.217.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.218.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.219.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.220.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.221.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.222.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.223.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.224.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.225.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.226.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.227.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.228.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.229.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.230.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.231.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.232.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.233.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.234.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.235.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.236.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.237.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.238.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.239.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.240.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.241.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.242.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.243.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.244.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.245.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.246.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.247.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.248.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.249.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.250.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.251.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.252.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.253.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.254.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
    '122.255.0.0/16': {'city': 'Various', 'country': 'India', 'isp': 'Airtel'},
}

def get_offline_location(ip_address):
    """Get location from offline database"""
    try:
        # Check exact IP match first
        if ip_address in IP_RANGES:
            info = IP_RANGES[ip_address]
            return {
                'location': f"{info['city']}, {info['country']}",
                'city': info['city'],
                'country': info['country'],
                'isp': info.get('isp', '')
            }
        
        # Check IP ranges
        ip_obj = ipaddress.ip_address(ip_address)
        for range_str, info in ISP_RANGES.items():
            try:
                network = ipaddress.ip_network(range_str)
                if ip_obj in network:
                    return {
                        'location': f"{info['city']}, {info['country']}",
                        'city': info['city'],
                        'country': info['country'],
                        'isp': info.get('isp', '')
                    }
            except ValueError:
                continue
                
    except Exception as e:
        print(f"Error in offline lookup: {e}")
    
    return None 