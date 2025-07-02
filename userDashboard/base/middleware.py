from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserLoginSession
from .ip_database import get_offline_location
from .wifi_location import WiFiLocationService
import requests
import json
import socket

class UserLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

@receiver(user_logged_in)
def user_login_handler(sender, request, user, **kwargs):
    """Handle user login and create session record"""
    try:
        # Get IP address
        ip_address = get_client_ip(request)
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get location information
        location_info = get_location_from_ip(ip_address)
        
        # Create login session
        UserLoginSession.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            location=location_info.get('location', ''),
            city=location_info.get('city', ''),
            country=location_info.get('country', ''),
            created_by=user
        )
    except Exception as e:
        # Log error but don't break the login process
        print(f"Error creating login session: {e}")

@receiver(user_logged_out)
def user_logout_handler(sender, request, user, **kwargs):
    """Handle user logout and update session record"""
    try:
        # Mark the most recent active session as logged out
        active_session = UserLoginSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-login_datetime').first()
        
        if active_session:
            active_session.is_active = False
            active_session.logout_datetime = timezone.now()
            active_session.save()
    except Exception as e:
        # Log error but don't break the logout process
        print(f"Error updating logout session: {e}")

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    # Additional headers to check
    if not ip or ip in ['127.0.0.1', 'localhost', '::1']:
        ip = request.META.get('HTTP_X_REAL_IP')
    if not ip or ip in ['127.0.0.1', 'localhost', '::1']:
        ip = request.META.get('HTTP_X_FORWARDED')
    if not ip or ip in ['127.0.0.1', 'localhost', '::1']:
        ip = request.META.get('HTTP_CLIENT_IP')
    
    return ip

def get_location_from_ip(ip_address):
    """Get location information from IP address using multiple methods"""
    # Handle localhost and private IPs
    if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
        # For localhost, try to get public IP for location
        try:
            public_ip = get_public_ip()
            if public_ip:
                print(f"Localhost detected, trying public IP: {public_ip}")
                return get_location_from_ip(public_ip)
        except Exception as e:
            print(f"Error getting public IP for localhost: {e}")
        
        return {
            'location': 'Local Development',
            'city': 'Local',
            'country': 'Development'
        }
    
    # Check if it's a private IP
    if is_private_ip(ip_address):
        # For private IPs, try to get public IP for location
        try:
            public_ip = get_public_ip()
            if public_ip and public_ip != ip_address:
                print(f"Private IP detected ({ip_address}), trying public IP: {public_ip}")
                return get_location_from_ip(public_ip)
        except Exception as e:
            print(f"Error getting public IP for private IP: {e}")
        
        return {
            'location': 'Private Network',
            'city': 'Private',
            'country': 'Network'
        }
    
    # For public IPs, try IP-based location first (more accurate for exact city/country)
    if not is_private_ip(ip_address):
        # Try multiple geolocation services
        services = [
            {
                'name': 'ipapi.co',
                'url': f'https://ipapi.co/{ip_address}/json/',
                'timeout': 5,
                'parser': lambda data: {
                    'location': f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country_name', '')}",
                    'city': data.get('city', ''),
                    'country': data.get('country_name', '')
                } if data.get('city') else None
            },
            {
                'name': 'ip-api.com',
                'url': f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting',
                'timeout': 5,
                'parser': lambda data: {
                    'location': f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}",
                    'city': data.get('city', ''),
                    'country': data.get('country', '')
                } if data.get('status') == 'success' else None
            },
            {
                'name': 'ipinfo.io',
                'url': f'https://ipinfo.io/{ip_address}/json',
                'timeout': 5,
                'parser': lambda data: {
                    'location': f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}",
                    'city': data.get('city', ''),
                    'country': data.get('country', '')
                } if data.get('city') else None
            }
        ]
        
        for service in services:
            try:
                print(f"Trying {service['name']} for IP: {ip_address}")
                response = requests.get(service['url'], timeout=service['timeout'])
                if response.status_code == 200:
                    data = response.json()
                    result = service['parser'](data)
                    if result and result.get('city') and result.get('city') != 'Unknown':
                        print(f"Success with {service['name']}: {result}")
                        return result
                    else:
                        print(f"Failed to parse response from {service['name']}")
                else:
                    print(f"HTTP {response.status_code} from {service['name']}")
            except Exception as e:
                print(f"Error with {service['name']}: {e}")
                continue
    
    # Try WiFi-based location as fallback (for private networks or when IP services fail)
    try:
        wifi_service = WiFiLocationService()
        wifi_networks = wifi_service.get_wifi_networks()
        if wifi_networks:
            wifi_location = wifi_service.get_location_from_wifi(wifi_networks)
            if wifi_location:
                print(f"WiFi location found: {wifi_location}")
                return {
                    'location': wifi_location['location'],
                    'city': wifi_location['city'],
                    'country': wifi_location['country']
                }
    except Exception as e:
        print(f"Error with WiFi location: {e}")
    
    # Try offline database as fallback
    offline_result = get_offline_location(ip_address)
    if offline_result:
        print(f"Found in offline database: {offline_result}")
        return {
            'location': offline_result['location'],
            'city': offline_result['city'],
            'country': offline_result['country']
        }
    
    # Ultimate fallback
    return {
        'location': f'IP: {ip_address}',
        'city': 'Unknown',
        'country': 'Unknown'
    }

def is_private_ip(ip):
    """Check if IP is private"""
    try:
        # Convert IP to integer for comparison
        ip_parts = ip.split('.')
        if len(ip_parts) != 4:
            return True
        
        first_octet = int(ip_parts[0])
        second_octet = int(ip_parts[1])
        
        # Private IP ranges
        if first_octet == 10:
            return True
        elif first_octet == 172 and 16 <= second_octet <= 31:
            return True
        elif first_octet == 192 and second_octet == 168:
            return True
        elif first_octet == 127:
            return True
        
        return False
    except:
        return True

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get('https://httpbin.org/ip', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('origin', '').split(',')[0].strip()
    except:
        pass
    return None 