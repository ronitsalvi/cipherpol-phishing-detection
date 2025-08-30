#!/usr/bin/env python3
"""
Comprehensive Network Diagnostics for Phishing Detection System
Identifies specific network connectivity issues affecting analysis modules
"""

import sys
import socket
import ssl
import dns.resolver
import dns.exception
import requests
import whois
import time
import subprocess
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional

class NetworkDiagnostics:
    """Comprehensive network connectivity testing"""
    
    def __init__(self):
        self.test_domains = [
            'github.com',
            'google.com', 
            'instagram.com',
            'httpbin.org'
        ]
        
        self.test_urls = [
            'https://github.com/new',
            'https://www.google.com',
            'https://www.instagram.com', 
            'https://httpbin.org/html'
        ]
        
        self.dns_servers = [
            '8.8.8.8',      # Google DNS
            '1.1.1.1',      # Cloudflare DNS  
            '208.67.222.222' # OpenDNS
        ]
    
    def run_full_diagnostics(self) -> Dict:
        """Run comprehensive network diagnostics"""
        
        print("🔍 NETWORK DIAGNOSTICS - Phishing Detection System")
        print("=" * 60)
        
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'basic_connectivity': {},
            'dns_resolution': {},
            'http_connectivity': {}, 
            'ssl_connectivity': {},
            'whois_connectivity': {},
            'system_info': {},
            'summary': {}
        }
        
        # Basic connectivity tests
        print("\n🌐 Basic Connectivity Tests")
        print("-" * 30)
        results['basic_connectivity'] = self._test_basic_connectivity()
        
        # DNS resolution tests
        print("\n📍 DNS Resolution Tests")
        print("-" * 30)
        results['dns_resolution'] = self._test_dns_resolution()
        
        # HTTP connectivity tests
        print("\n🔗 HTTP Connectivity Tests") 
        print("-" * 30)
        results['http_connectivity'] = self._test_http_connectivity()
        
        # SSL connectivity tests
        print("\n🔒 SSL Connectivity Tests")
        print("-" * 30)
        results['ssl_connectivity'] = self._test_ssl_connectivity()
        
        # WHOIS connectivity tests
        print("\n📋 WHOIS Connectivity Tests")
        print("-" * 30)
        results['whois_connectivity'] = self._test_whois_connectivity()
        
        # System information
        print("\n⚙️  System Information")
        print("-" * 30)
        results['system_info'] = self._get_system_info()
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTICS SUMMARY")
        print("=" * 60)
        self._print_summary(results['summary'])
        
        return results
    
    def _test_basic_connectivity(self) -> Dict:
        """Test basic network connectivity"""
        
        results = {}
        
        # Test internet connectivity
        print("Testing internet connectivity...")
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            results['internet'] = {'status': 'SUCCESS', 'message': 'Internet connectivity available'}
            print("✅ Internet: Connected")
        except Exception as e:
            results['internet'] = {'status': 'FAILED', 'message': f'No internet: {e}'}
            print(f"❌ Internet: Failed - {e}")
        
        # Test DNS connectivity
        print("Testing DNS connectivity...")
        try:
            socket.getaddrinfo('google.com', 80)
            results['dns_basic'] = {'status': 'SUCCESS', 'message': 'DNS resolution working'}
            print("✅ DNS: Working")
        except Exception as e:
            results['dns_basic'] = {'status': 'FAILED', 'message': f'DNS failed: {e}'}
            print(f"❌ DNS: Failed - {e}")
        
        return results
    
    def _test_dns_resolution(self) -> Dict:
        """Test DNS resolution with different servers"""
        
        results = {}
        
        # Test with different DNS servers
        for dns_server in self.dns_servers:
            print(f"Testing DNS server {dns_server}...")
            results[dns_server] = {}
            
            # Configure resolver
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = 10
            resolver.lifetime = 10
            
            for domain in self.test_domains:
                try:
                    start_time = time.time()
                    answer = resolver.resolve(domain, 'A')
                    duration = time.time() - start_time
                    
                    ips = [str(rdata) for rdata in answer]
                    results[dns_server][domain] = {
                        'status': 'SUCCESS',
                        'ips': ips,
                        'duration': round(duration, 3),
                        'message': f'Resolved to {len(ips)} IPs in {duration:.3f}s'
                    }
                    print(f"  ✅ {domain}: {ips[0]} ({duration:.3f}s)")
                    
                except dns.exception.Timeout:
                    results[dns_server][domain] = {
                        'status': 'TIMEOUT',
                        'message': 'DNS query timed out'
                    }
                    print(f"  ⏰ {domain}: Timeout")
                    
                except dns.exception.DNSException as e:
                    results[dns_server][domain] = {
                        'status': 'FAILED', 
                        'message': f'DNS error: {e}'
                    }
                    print(f"  ❌ {domain}: {e}")
                    
                except Exception as e:
                    results[dns_server][domain] = {
                        'status': 'ERROR',
                        'message': f'Unexpected error: {e}'
                    }
                    print(f"  💥 {domain}: {e}")
        
        return results
    
    def _test_http_connectivity(self) -> Dict:
        """Test HTTP/HTTPS connectivity"""
        
        results = {}
        
        # Test with different configurations
        session_configs = {
            'default': {'timeout': 15},
            'long_timeout': {'timeout': 30},
            'with_headers': {
                'timeout': 15,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Phishing Detection System)',
                    'Accept': 'text/html,application/xhtml+xml'
                }
            }
        }
        
        for config_name, config in session_configs.items():
            print(f"Testing HTTP with {config_name} config...")
            results[config_name] = {}
            
            session = requests.Session()
            
            for url in self.test_urls:
                try:
                    start_time = time.time()
                    response = session.get(url, **config)
                    duration = time.time() - start_time
                    
                    results[config_name][url] = {
                        'status': 'SUCCESS',
                        'status_code': response.status_code,
                        'duration': round(duration, 3),
                        'content_length': len(response.content),
                        'message': f'{response.status_code} in {duration:.3f}s ({len(response.content)} bytes)'
                    }
                    print(f"  ✅ {url}: {response.status_code} ({duration:.3f}s)")
                    
                except requests.exceptions.Timeout:
                    results[config_name][url] = {
                        'status': 'TIMEOUT',
                        'message': 'Request timed out'
                    }
                    print(f"  ⏰ {url}: Timeout")
                    
                except requests.exceptions.ConnectionError as e:
                    results[config_name][url] = {
                        'status': 'CONNECTION_ERROR',
                        'message': f'Connection failed: {e}'
                    }
                    print(f"  🔌 {url}: Connection Error")
                    
                except requests.exceptions.RequestException as e:
                    results[config_name][url] = {
                        'status': 'FAILED',
                        'message': f'Request failed: {e}'
                    }
                    print(f"  ❌ {url}: {e}")
                    
                except Exception as e:
                    results[config_name][url] = {
                        'status': 'ERROR', 
                        'message': f'Unexpected error: {e}'
                    }
                    print(f"  💥 {url}: {e}")
        
        return results
    
    def _test_ssl_connectivity(self) -> Dict:
        """Test SSL/TLS connectivity"""
        
        results = {}
        
        for domain in self.test_domains:
            print(f"Testing SSL for {domain}...")
            try:
                start_time = time.time()
                
                # Create SSL context
                context = ssl.create_default_context()
                
                # Connect and get certificate
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        cipher = ssock.cipher()
                        
                duration = time.time() - start_time
                
                results[domain] = {
                    'status': 'SUCCESS',
                    'duration': round(duration, 3),
                    'cipher': cipher[0] if cipher else 'Unknown',
                    'tls_version': cipher[1] if cipher else 'Unknown', 
                    'cert_subject': dict(x[0] for x in cert['subject']),
                    'cert_issuer': dict(x[0] for x in cert['issuer']),
                    'message': f'SSL connected in {duration:.3f}s'
                }
                print(f"  ✅ {domain}: {cipher[1]} ({duration:.3f}s)")
                
            except ssl.SSLError as e:
                results[domain] = {
                    'status': 'SSL_ERROR',
                    'message': f'SSL error: {e}'
                }
                print(f"  🔒 {domain}: SSL Error - {e}")
                
            except socket.timeout:
                results[domain] = {
                    'status': 'TIMEOUT',
                    'message': 'SSL connection timed out'
                }
                print(f"  ⏰ {domain}: Timeout")
                
            except Exception as e:
                results[domain] = {
                    'status': 'ERROR',
                    'message': f'Unexpected error: {e}'
                }
                print(f"  💥 {domain}: {e}")
        
        return results
    
    def _test_whois_connectivity(self) -> Dict:
        """Test WHOIS connectivity"""
        
        results = {}
        
        for domain in self.test_domains:
            print(f"Testing WHOIS for {domain}...")
            try:
                start_time = time.time()
                domain_info = whois.whois(domain)
                duration = time.time() - start_time
                
                creation_date = domain_info.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                results[domain] = {
                    'status': 'SUCCESS',
                    'duration': round(duration, 3),
                    'creation_date': str(creation_date) if creation_date else 'Unknown',
                    'registrar': domain_info.registrar or 'Unknown',
                    'message': f'WHOIS data retrieved in {duration:.3f}s'
                }
                print(f"  ✅ {domain}: {domain_info.registrar} ({duration:.3f}s)")
                
            except Exception as e:
                results[domain] = {
                    'status': 'FAILED',
                    'message': f'WHOIS failed: {e}'
                }
                print(f"  ❌ {domain}: {e}")
        
        return results
    
    def _get_system_info(self) -> Dict:
        """Get system information"""
        
        info = {
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        # Test DNS configuration
        try:
            result = subprocess.run(['cat', '/etc/resolv.conf'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                info['dns_config'] = result.stdout.strip()
            else:
                info['dns_config'] = 'Unable to read DNS config'
        except:
            info['dns_config'] = 'DNS config not available'
        
        # Network interface info
        try:
            result = subprocess.run(['ifconfig'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Extract just the interface names and IP addresses
                lines = result.stdout.split('\n')
                interfaces = []
                for line in lines:
                    if 'inet ' in line and '127.0.0.1' not in line:
                        interfaces.append(line.strip())
                info['network_interfaces'] = interfaces[:5]  # Limit output
            else:
                info['network_interfaces'] = 'Interface info not available'
        except:
            info['network_interfaces'] = 'Interface info not available'
        
        print(f"Python: {sys.version.split()[0]}")
        print(f"Platform: {sys.platform}")
        
        return info
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate diagnostic summary"""
        
        summary = {
            'overall_status': 'UNKNOWN',
            'issues_found': [],
            'working_components': [],
            'recommendations': []
        }
        
        # Analyze basic connectivity
        if results['basic_connectivity'].get('internet', {}).get('status') != 'SUCCESS':
            summary['issues_found'].append('No internet connectivity')
        else:
            summary['working_components'].append('Internet connectivity')
        
        if results['basic_connectivity'].get('dns_basic', {}).get('status') != 'SUCCESS':
            summary['issues_found'].append('Basic DNS resolution failed')
        else:
            summary['working_components'].append('Basic DNS resolution')
        
        # Analyze DNS servers
        working_dns = 0
        for dns_server in self.dns_servers:
            if dns_server in results['dns_resolution']:
                working_domains = sum(1 for domain_result in results['dns_resolution'][dns_server].values() 
                                    if domain_result.get('status') == 'SUCCESS')
                if working_domains > 0:
                    working_dns += 1
        
        if working_dns == 0:
            summary['issues_found'].append('No DNS servers working')
        else:
            summary['working_components'].append(f'{working_dns}/{len(self.dns_servers)} DNS servers working')
        
        # Analyze HTTP connectivity
        working_http = 0
        for config in results['http_connectivity']:
            working_urls = sum(1 for url_result in results['http_connectivity'][config].values()
                             if url_result.get('status') == 'SUCCESS')
            if working_urls > 0:
                working_http += 1
        
        if working_http == 0:
            summary['issues_found'].append('No HTTP connectivity')
        else:
            summary['working_components'].append('HTTP connectivity working')
        
        # Analyze SSL connectivity  
        working_ssl = sum(1 for ssl_result in results['ssl_connectivity'].values()
                         if ssl_result.get('status') == 'SUCCESS')
        
        if working_ssl == 0:
            summary['issues_found'].append('No SSL connectivity')
        else:
            summary['working_components'].append(f'SSL working for {working_ssl}/{len(self.test_domains)} domains')
        
        # Analyze WHOIS connectivity
        working_whois = sum(1 for whois_result in results['whois_connectivity'].values()
                           if whois_result.get('status') == 'SUCCESS')
        
        if working_whois == 0:
            summary['issues_found'].append('No WHOIS connectivity')
        else:
            summary['working_components'].append(f'WHOIS working for {working_whois}/{len(self.test_domains)} domains')
        
        # Determine overall status
        if len(summary['issues_found']) == 0:
            summary['overall_status'] = 'EXCELLENT'
        elif len(summary['working_components']) > len(summary['issues_found']):
            summary['overall_status'] = 'PARTIAL'
        else:
            summary['overall_status'] = 'POOR'
        
        # Generate recommendations
        if 'No internet connectivity' in summary['issues_found']:
            summary['recommendations'].append('Check network connection and try again')
        if 'No DNS servers working' in summary['issues_found']:
            summary['recommendations'].append('Try different DNS servers (8.8.8.8, 1.1.1.1)')
        if 'No HTTP connectivity' in summary['issues_found']:
            summary['recommendations'].append('Check firewall and proxy settings')
        if 'No SSL connectivity' in summary['issues_found']:
            summary['recommendations'].append('Check SSL/TLS configuration and certificates')
        if 'No WHOIS connectivity' in summary['issues_found']:
            summary['recommendations'].append('WHOIS servers may be blocked or rate-limiting')
        
        return summary
    
    def _print_summary(self, summary: Dict):
        """Print diagnostic summary"""
        
        status_emoji = {
            'EXCELLENT': '🟢',
            'PARTIAL': '🟡', 
            'POOR': '🔴',
            'UNKNOWN': '⚪'
        }
        
        print(f"\n{status_emoji.get(summary['overall_status'], '⚪')} Overall Status: {summary['overall_status']}")
        
        if summary['working_components']:
            print(f"\n✅ Working Components:")
            for component in summary['working_components']:
                print(f"   • {component}")
        
        if summary['issues_found']:
            print(f"\n❌ Issues Found:")
            for issue in summary['issues_found']:
                print(f"   • {issue}")
        
        if summary['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"   • {rec}")

def main():
    """Run network diagnostics"""
    diagnostics = NetworkDiagnostics()
    results = diagnostics.run_full_diagnostics()
    
    # Save results
    import json
    with open('/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1/diagnostics/network_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: network_test_results.json")

if __name__ == "__main__":
    main()