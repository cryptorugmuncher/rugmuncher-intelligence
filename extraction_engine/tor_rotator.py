#!/usr/bin/env python3
"""
Tor IP Rotation System
Free, unlimited IP rotation for scraping
"""
import requests
import time
import logging
from typing import Optional, Dict
import subprocess
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TorRotator:
    """
    Manages Tor connection for IP rotation
    Requires Tor to be installed: apt-get install tor
    """
    
    def __init__(self, control_port: int = 9051, proxy_port: int = 9050):
        self.control_port = control_port
        self.proxy_port = proxy_port
        self.proxy = {
            'http': f'socks5h://127.0.0.1:{proxy_port}',
            'https': f'socks5h://127.0.0.1:{proxy_port}'
        }
        self.controller = None
        self.request_count = 0
        self.rotation_interval = 10  # Rotate every N requests
        
    def start_tor(self):
        """Start Tor service if not running"""
        try:
            # Check if Tor is running
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', self.proxy_port))
            sock.close()
            
            if result != 0:
                logger.info("Starting Tor service...")
                subprocess.run(['service', 'tor', 'start'], check=True)
                time.sleep(5)  # Wait for Tor to start
            else:
                logger.info("Tor is already running")
                
        except Exception as e:
            logger.error(f"Failed to start Tor: {e}")
            logger.info("Install Tor: apt-get install tor")
    
    def new_identity(self):
        """Get new Tor exit node (new IP)"""
        try:
            from stem import Signal
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                time.sleep(5)  # Wait for new circuit
                
            logger.info("New Tor identity established")
            self.request_count = 0
            
        except Exception as e:
            logger.error(f"Failed to get new identity: {e}")
    
    def get_current_ip(self) -> Optional[str]:
        """Get current exit IP address"""
        try:
            response = requests.get(
                'https://check.torproject.org/api/ip',
                proxies=self.proxy,
                timeout=30
            )
            data = response.json()
            return data.get('IP')
        except Exception as e:
            logger.error(f"Failed to get IP: {e}")
            return None
    
    def request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make request through Tor with automatic rotation
        """
        # Rotate IP every N requests
        if self.request_count >= self.rotation_interval:
            self.new_identity()
        
        try:
            kwargs['proxies'] = self.proxy
            kwargs['timeout'] = kwargs.get('timeout', 30)
            
            response = requests.request(method, url, **kwargs)
            self.request_count += 1
            
            # If blocked, rotate immediately
            if response.status_code in [403, 429]:
                logger.warning(f"Blocked (status {response.status_code}), rotating...")
                self.new_identity()
                return self.request(url, method, **kwargs)
            
            return response
            
        except requests.exceptions.ProxyError as e:
            logger.error(f"Tor proxy error: {e}")
            self.new_identity()
            return self.request(url, method, **kwargs)
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if Tor is working"""
        try:
            ip = self.get_current_ip()
            if ip:
                logger.info(f"Tor is working. Exit IP: {ip}")
                return True
            return False
        except:
            return False


class MultiTorManager:
    """
    Manage multiple Tor instances for even more IPs
    Advanced: Run multiple Tor instances on different ports
    """
    
    def __init__(self):
        self.tor_instances = []
        self.current = 0
    
    def add_instance(self, control_port: int, proxy_port: int):
        """Add another Tor instance"""
        tor = TorRotator(control_port, proxy_port)
        self.tor_instances.append(tor)
    
    def request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Round-robin through Tor instances"""
        tor = self.tor_instances[self.current % len(self.tor_instances)]
        self.current += 1
        return tor.request(url, **kwargs)


# Free proxy list updater
class FreeProxyManager:
    """
    Manages free proxy lists for additional rotation
    """
    
    PROXY_SOURCES = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    ]
    
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.last_update = 0
        
    def update_proxies(self, max_proxies: int = 100):
        """Fetch fresh proxy list"""
        import random
        
        logger.info("Updating free proxy list...")
        new_proxies = []
        
        for source in self.PROXY_SOURCES:
            try:
                response = requests.get(source, timeout=10)
                lines = [line.strip() for line in response.text.split('\n') if line.strip()]
                new_proxies.extend(lines)
            except Exception as e:
                logger.warning(f"Failed to fetch from {source}: {e}")
        
        # Remove duplicates and limit
        self.proxies = list(set(new_proxies))[:max_proxies]
        logger.info(f"Fetched {len(self.proxies)} proxies")
        
        # Test a sample
        self._test_proxy_sample()
    
    def _test_proxy_sample(self, sample_size: int = 20):
        """Test a sample of proxies"""
        import random
        sample = random.sample(self.proxies, min(sample_size, len(self.proxies)))
        
        working = []
        for proxy in sample:
            try:
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                response = requests.get(
                    'https://httpbin.org/ip',
                    proxies=proxy_dict,
                    timeout=5
                )
                if response.status_code == 200:
                    working.append(proxy)
            except:
                pass
        
        self.working_proxies = working
        logger.info(f"Found {len(working)} working proxies from sample")
    
    def get_proxy(self) -> Optional[Dict]:
        """Get a random working proxy"""
        if not self.working_proxies:
            self.update_proxies()
        
        if self.working_proxies:
            proxy = random.choice(self.working_proxies)
            return {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
        return None


if __name__ == "__main__":
    # Test Tor rotator
    print("Testing Tor Rotator...")
    
    tor = TorRotator()
    tor.start_tor()
    
    if tor.test_connection():
        print("✅ Tor is working!")
        
        # Make test request
        response = tor.request('https://check.torproject.org/api/ip')
        if response:
            print(f"Response: {response.json()}")
    else:
        print("❌ Tor is not working. Install with: apt-get install tor")
