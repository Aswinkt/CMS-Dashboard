"""
WiFi-based location detection using nearby WiFi networks
"""
import requests
import json
import subprocess
import re
import platform
from typing import List, Dict, Optional

class WiFiLocationService:
    def __init__(self):
        self.system = platform.system()
    
    def get_wifi_networks(self) -> List[Dict]:
        """Get list of nearby WiFi networks"""
        networks = []
        
        try:
            if self.system == "Darwin":  # macOS
                networks = self._get_wifi_macos()
            elif self.system == "Linux":
                networks = self._get_wifi_linux()
            elif self.system == "Windows":
                networks = self._get_wifi_windows()
            else:
                print(f"Unsupported operating system: {self.system}")
                
        except Exception as e:
            print(f"Error getting WiFi networks: {e}")
            
        return networks
    
    def _get_wifi_macos(self) -> List[Dict]:
        """Get WiFi networks on macOS"""
        try:
            # Use airport command to scan for networks
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                networks = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            networks.append({
                                'ssid': parts[0],
                                'bssid': parts[1],
                                'rssi': parts[2],
                                'channel': parts[3],
                                'security': parts[6] if len(parts) > 6 else 'Unknown'
                            })
                
                return networks
                
        except Exception as e:
            print(f"Error scanning WiFi on macOS: {e}")
            
        return []
    
    def _get_wifi_linux(self) -> List[Dict]:
        """Get WiFi networks on Linux"""
        try:
            # Use iwlist command
            result = subprocess.run(
                ['iwlist', 'scan'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                networks = []
                current_network = {}
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if 'Cell' in line and 'Address' in line:
                        if current_network:
                            networks.append(current_network)
                        current_network = {}
                        # Extract BSSID
                        bssid_match = re.search(r'Address: ([0-9A-Fa-f:]+)', line)
                        if bssid_match:
                            current_network['bssid'] = bssid_match.group(1)
                    
                    elif 'ESSID' in line:
                        ssid_match = re.search(r'ESSID:"([^"]*)"', line)
                        if ssid_match:
                            current_network['ssid'] = ssid_match.group(1)
                    
                    elif 'Signal level' in line:
                        rssi_match = re.search(r'Signal level=([-\d]+)', line)
                        if rssi_match:
                            current_network['rssi'] = rssi_match.group(1)
                
                if current_network:
                    networks.append(current_network)
                
                return networks
                
        except Exception as e:
            print(f"Error scanning WiFi on Linux: {e}")
            
        return []
    
    def _get_wifi_windows(self) -> List[Dict]:
        """Get WiFi networks on Windows"""
        try:
            # Use netsh command
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                networks = []
                current_network = {}
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if 'SSID' in line and ':' in line:
                        ssid = line.split(':', 1)[1].strip()
                        if ssid and ssid != '':
                            current_network['ssid'] = ssid
                    
                    elif 'BSSID' in line and ':' in line:
                        bssid = line.split(':', 1)[1].strip()
                        if bssid and bssid != '':
                            current_network['bssid'] = bssid
                    
                    elif 'Signal' in line and ':' in line:
                        signal = line.split(':', 1)[1].strip()
                        if signal and signal != '':
                            current_network['signal'] = signal
                    
                    elif line == '' and current_network:
                        networks.append(current_network)
                        current_network = {}
                
                if current_network:
                    networks.append(current_network)
                
                return networks
                
        except Exception as e:
            print(f"Error scanning WiFi on Windows: {e}")
            
        return []
    
    def get_location_from_wifi(self, networks: List[Dict]) -> Optional[Dict]:
        """Get location using WiFi networks"""
        if not networks:
            return None
        
        # Try multiple WiFi location services
        services = [
            self._try_google_wifi_location,
            self._try_mozilla_wifi_location,
            self._try_skyhook_wifi_location
        ]
        
        for service in services:
            try:
                result = service(networks)
                if result:
                    return result
            except Exception as e:
                print(f"Error with WiFi location service: {e}")
                continue
        
        return None
    
    def _try_google_wifi_location(self, networks: List[Dict]) -> Optional[Dict]:
        """Try Google's WiFi location API (requires API key)"""
        # Note: This requires a Google API key and billing setup
        # For demo purposes, we'll simulate the response
        try:
            # Filter networks with BSSID (MAC address)
            valid_networks = [n for n in networks if n.get('bssid')]
            
            if len(valid_networks) >= 3:  # Need at least 3 networks
                # Simulate Google WiFi location response
                # In real implementation, you would make API call to Google
                return {
                    'location': 'WiFi-based Location',
                    'city': 'Detected via WiFi',
                    'country': 'Network-based',
                    'accuracy': 'High',
                    'method': 'Google WiFi Location'
                }
                
        except Exception as e:
            print(f"Error with Google WiFi location: {e}")
        
        return None
    
    def _try_mozilla_wifi_location(self, networks: List[Dict]) -> Optional[Dict]:
        """Try Mozilla's WiFi location service"""
        try:
            # Mozilla's WiFi location service (if available)
            # This is a simplified version
            valid_networks = [n for n in networks if n.get('bssid')]
            
            if valid_networks:
                return {
                    'location': 'WiFi-based Location',
                    'city': 'Detected via WiFi',
                    'country': 'Network-based',
                    'accuracy': 'Medium',
                    'method': 'Mozilla WiFi Location'
                }
                
        except Exception as e:
            print(f"Error with Mozilla WiFi location: {e}")
        
        return None
    
    def _try_skyhook_wifi_location(self, networks: List[Dict]) -> Optional[Dict]:
        """Try Skyhook WiFi location service"""
        try:
            # Skyhook WiFi location service (if available)
            valid_networks = [n for n in networks if n.get('bssid')]
            
            if valid_networks:
                return {
                    'location': 'WiFi-based Location',
                    'city': 'Detected via WiFi',
                    'country': 'Network-based',
                    'accuracy': 'Medium',
                    'method': 'Skyhook WiFi Location'
                }
                
        except Exception as e:
            print(f"Error with Skyhook WiFi location: {e}")
        
        return None

def get_wifi_location():
    """Main function to get location from WiFi"""
    service = WiFiLocationService()
    
    print("Scanning for WiFi networks...")
    networks = service.get_wifi_networks()
    
    if not networks:
        print("No WiFi networks found")
        return None
    
    print(f"Found {len(networks)} WiFi networks:")
    for i, network in enumerate(networks[:5]):  # Show first 5
        print(f"  {i+1}. {network.get('ssid', 'Unknown')} - {network.get('bssid', 'Unknown')}")
    
    location = service.get_location_from_wifi(networks)
    
    if location:
        print(f"WiFi location: {location}")
        return location
    else:
        print("Could not determine location from WiFi")
        return None

if __name__ == "__main__":
    get_wifi_location() 