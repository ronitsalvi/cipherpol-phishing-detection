"""
Technical Analyzer Module
Analyzes technical infrastructure characteristics for phishing detection
"""

import socket
import ssl
import dns.resolver
import dns.exception
import requests
from urllib.parse import urlparse
import datetime
from typing import Dict, List, Optional
import logging
import ipaddress
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Analyzes technical infrastructure for phishing indicators"""
    
    def __init__(self):
        # Known hosting providers with reputation scores (1-5, higher = more trusted)
        self.hosting_reputation = {
            'amazon': 5, 'google': 5, 'microsoft': 5, 'cloudflare': 5,
            'akamai': 4, 'fastly': 4, 'netlify': 4, 'github': 5,
            'digitalocean': 3, 'linode': 3, 'vultr': 3,
            'godaddy': 2, 'namecheap': 2, 'hostgator': 2,
            'unknown': 1
        }
        
        # Suspicious hosting patterns
        self.suspicious_hosts = {
            'bulletproof', 'anonymous', 'privacy', 'offshore',
            'secure-server', 'private-host'
        }
        
        # High-risk countries for hosting (based on common phishing origins)
        self.high_risk_countries = {
            'CN', 'RU', 'TR', 'PK', 'BD', 'VN', 'UA', 'RO', 'BG'
        }
    
    def analyze_technical(self, url: str) -> Dict:
        """Perform comprehensive technical analysis"""
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if not domain:
                return {'error': 'Invalid URL format'}
            
            results = {
                'domain': domain,
                'url': url,
                'score': 0,
                'explanations': []
            }
            
            # Analyze different technical aspects
            self._analyze_ssl_security(domain, results)
            self._analyze_dns_configuration(domain, results)
            self._analyze_hosting_characteristics(domain, results)
            self._analyze_response_characteristics(url, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {url}: {e}")
            return {'error': str(e)}
    
    def _analyze_ssl_security(self, domain: str, results: Dict):
        """Analyze SSL certificate security characteristics"""
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Get certificate information
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    # Certificate is present and valid
                    points = 8
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': 'Valid SSL certificate installed',
                        'points': points,
                        'evidence': f'Certificate verified for {domain}'
                    })
                    
                    # Analyze certificate details
                    self._analyze_certificate_details(cert, results)
                    self._analyze_ssl_cipher(cipher, results)
                    
        except ssl.SSLError as e:
            points = -15
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'SSL certificate error or invalid',
                'points': abs(points),
                'evidence': f'SSL Error: {str(e)[:100]}'
            })
        except (socket.timeout, socket.gaierror, ConnectionRefusedError):
            points = -12
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'No HTTPS support or connection failed',
                'points': abs(points),
                'evidence': 'Cannot establish secure connection'
            })
        except Exception as e:
            logger.debug(f"SSL analysis failed for {domain}: {e}")
    
    def _analyze_certificate_details(self, cert: Dict, results: Dict):
        """Analyze SSL certificate specific details"""
        
        try:
            # Certificate expiry analysis
            not_after = cert.get('notAfter')
            if not_after:
                expiry_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.datetime.now()).days
                
                if days_until_expiry < 7:
                    points = -8
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'SSL certificate expires very soon ({days_until_expiry} days)',
                        'points': abs(points),
                        'evidence': f'Expires: {expiry_date.strftime("%Y-%m-%d")}'
                    })
                elif days_until_expiry < 30:
                    points = -4
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'SSL certificate expires soon ({days_until_expiry} days)',
                        'points': abs(points),
                        'evidence': f'Expires: {expiry_date.strftime("%Y-%m-%d")}'
                    })
            
            # Certificate age analysis
            not_before = cert.get('notBefore')
            if not_before:
                issued_date = datetime.datetime.strptime(not_before, '%b %d %H:%M:%S %Y %Z')
                cert_age_days = (datetime.datetime.now() - issued_date).days
                
                if cert_age_days < 7:
                    points = -6
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Very new SSL certificate ({cert_age_days} days old)',
                        'points': abs(points),
                        'evidence': f'Issued: {issued_date.strftime("%Y-%m-%d")}'
                    })
            
            # Certificate issuer analysis
            issuer = cert.get('issuer', ())
            issuer_cn = None
            
            for item in issuer:
                if item[0][0] == 'commonName':
                    issuer_cn = item[0][1]
                    break
            
            if issuer_cn:
                trusted_issuers = [
                    'let\'s encrypt', 'digicert', 'comodo', 'symantec', 'globalsign',
                    'godaddy', 'thawte', 'verisign', 'rapidssl', 'sectigo'
                ]
                
                issuer_lower = issuer_cn.lower()
                is_trusted = any(trusted in issuer_lower for trusted in trusted_issuers)
                
                if is_trusted:
                    points = 3
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': f'Certificate from trusted issuer: {issuer_cn}',
                        'points': points,
                        'evidence': 'Recognized certificate authority'
                    })
                else:
                    results['explanations'].append({
                        'type': 'neutral',
                        'description': f'Certificate issuer: {issuer_cn}',
                        'evidence': 'Certificate authority not in common list'
                    })
            
        except Exception as e:
            logger.debug(f"Certificate detail analysis failed: {e}")
    
    def _analyze_ssl_cipher(self, cipher: tuple, results: Dict):
        """Analyze SSL cipher strength"""
        
        try:
            if cipher:
                cipher_suite = cipher[0] if len(cipher) > 0 else ''
                protocol = cipher[1] if len(cipher) > 1 else ''
                key_length = cipher[2] if len(cipher) > 2 else 0
                
                # Check protocol version
                if protocol in ['TLSv1.3', 'TLSv1.2']:
                    points = 2
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': f'Modern SSL protocol: {protocol}',
                        'points': points,
                        'evidence': f'Protocol: {protocol}'
                    })
                elif protocol in ['TLSv1.1', 'TLSv1.0']:
                    points = -3
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Outdated SSL protocol: {protocol}',
                        'points': abs(points),
                        'evidence': f'Protocol: {protocol}'
                    })
                
                # Check key length
                if key_length >= 256:
                    points = 2
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': f'Strong encryption: {key_length}-bit',
                        'points': points,
                        'evidence': f'Key length: {key_length} bits'
                    })
                elif key_length < 128:
                    points = -5
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Weak encryption: {key_length}-bit',
                        'points': abs(points),
                        'evidence': f'Key length: {key_length} bits'
                    })
                    
        except Exception as e:
            logger.debug(f"SSL cipher analysis failed: {e}")
    
    def _analyze_dns_configuration(self, domain: str, results: Dict):
        """Analyze DNS configuration patterns"""
        
        try:
            # Check for various DNS record types
            has_records = {
                'A': False, 'AAAA': False, 'MX': False, 
                'TXT': False, 'NS': False, 'CNAME': False
            }
            
            record_details = {}
            
            # Check A record
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                has_records['A'] = True
                record_details['A'] = [str(record) for record in a_records]
                
                # Analyze IP addresses
                self._analyze_ip_addresses(record_details['A'], results)
                
            except dns.exception.DNSException:
                pass
            
            # Check AAAA record (IPv6)
            try:
                aaaa_records = dns.resolver.resolve(domain, 'AAAA')
                has_records['AAAA'] = True
            except dns.exception.DNSException:
                pass
            
            # Check MX record
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                has_records['MX'] = True
                record_details['MX'] = [str(record) for record in mx_records]
            except dns.exception.DNSException:
                pass
            
            # Check TXT record
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                has_records['TXT'] = True
                record_details['TXT'] = [str(record) for record in txt_records]
            except dns.exception.DNSException:
                pass
            
            # Check NS record
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                has_records['NS'] = True
                record_details['NS'] = [str(record) for record in ns_records]
            except dns.exception.DNSException:
                pass
            
            # Score based on DNS completeness
            record_count = sum(has_records.values())
            
            if record_count >= 4:  # Has A, MX, TXT, NS at minimum
                points = 6
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': f'Complete DNS configuration ({record_count}/6 record types)',
                    'points': points,
                    'evidence': f'Records present: {", ".join(k for k, v in has_records.items() if v)}'
                })
            elif record_count >= 2:
                points = 2
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': f'Basic DNS configuration ({record_count}/6 record types)',
                    'points': points,
                    'evidence': f'Records present: {", ".join(k for k, v in has_records.items() if v)}'
                })
            else:
                points = -8
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Minimal DNS configuration ({record_count}/6 record types)',
                    'points': abs(points),
                    'evidence': 'Missing important DNS records'
                })
            
        except Exception as e:
            logger.debug(f"DNS analysis failed for {domain}: {e}")
    
    def _analyze_ip_addresses(self, ip_addresses: List[str], results: Dict):
        """Analyze IP address characteristics"""
        
        try:
            for ip_str in ip_addresses:
                ip = ipaddress.ip_address(ip_str)
                
                # Check for private IP addresses (suspicious for public websites)
                if ip.is_private:
                    points = -10
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Uses private IP address: {ip_str}',
                        'points': abs(points),
                        'evidence': 'Private IPs not suitable for public websites'
                    })
                
                # Check for localhost
                elif ip.is_loopback:
                    points = -15
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Points to localhost: {ip_str}',
                        'points': abs(points),
                        'evidence': 'Localhost IP detected'
                    })
                
                # Try to get geographic information (simplified version)
                # Note: In production, you'd want to use a proper GeoIP database
                self._analyze_ip_geolocation(ip_str, results)
                
        except Exception as e:
            logger.debug(f"IP address analysis failed: {e}")
    
    def _analyze_ip_geolocation(self, ip_str: str, results: Dict):
        """Analyze IP geolocation (simplified without external database)"""
        
        try:
            # This is a simplified approach - in production use proper GeoIP database
            # For now, we'll do basic checks
            
            # Check if IP is in commonly used cloud provider ranges (simplified)
            # These are rough approximations - use proper IP range databases in production
            ip_int = int(ipaddress.ip_address(ip_str))
            
            # Very basic cloud provider detection (this would be much more comprehensive in production)
            cloud_indicators = {
                'AWS': False,
                'Google': False,
                'Cloudflare': False,
                'Microsoft': False
            }
            
            # This is just a placeholder - proper implementation would use WHOIS or IP range databases
            results['explanations'].append({
                'type': 'neutral',
                'description': f'IP address: {ip_str}',
                'evidence': 'Geographic analysis requires external database'
            })
            
        except Exception as e:
            logger.debug(f"IP geolocation analysis failed: {e}")
    
    def _analyze_hosting_characteristics(self, domain: str, results: Dict):
        """Analyze hosting provider characteristics"""
        
        try:
            # Get IP addresses for the domain
            a_records = dns.resolver.resolve(domain, 'A')
            ip_addresses = [str(record) for record in a_records]
            
            for ip in ip_addresses:
                self._analyze_hosting_provider(ip, results)
                
        except dns.exception.DNSException:
            points = -5
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'Unable to resolve domain to IP address',
                'points': abs(points),
                'evidence': 'DNS resolution failed'
            })
        except Exception as e:
            logger.debug(f"Hosting analysis failed for {domain}: {e}")
    
    def _analyze_hosting_provider(self, ip: str, results: Dict):
        """Analyze specific hosting provider characteristics"""
        
        try:
            # This is simplified - in production you'd use WHOIS or ASN databases
            # For now, we'll do basic pattern matching
            
            # Placeholder for hosting provider detection
            # In production, use services like IPinfo, MaxMind, or WHOIS databases
            
            results['explanations'].append({
                'type': 'neutral',
                'description': f'Hosted on IP: {ip}',
                'evidence': 'Hosting provider analysis requires external database'
            })
            
        except Exception as e:
            logger.debug(f"Hosting provider analysis failed: {e}")
    
    def _analyze_response_characteristics(self, url: str, results: Dict):
        """Analyze HTTP response characteristics"""
        
        try:
            # Make request to analyze response
            response = requests.head(url, timeout=10, allow_redirects=False, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Analyze response headers
            self._analyze_response_headers(response.headers, results)
            
            # Analyze redirects
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location:
                    self._analyze_redirect(url, location, results)
            
        except requests.RequestException as e:
            points = -3
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'HTTP request failed: {str(e)[:50]}',
                'points': abs(points),
                'evidence': 'Server connection issues'
            })
        except Exception as e:
            logger.debug(f"Response analysis failed: {e}")
    
    def _analyze_response_headers(self, headers: Dict, results: Dict):
        """Analyze HTTP response headers"""
        
        try:
            security_headers = {
                'Strict-Transport-Security': 'HSTS header',
                'Content-Security-Policy': 'CSP header',
                'X-Frame-Options': 'X-Frame-Options header',
                'X-Content-Type-Options': 'X-Content-Type-Options header'
            }
            
            present_security_headers = []
            
            for header, description in security_headers.items():
                if header in headers:
                    present_security_headers.append(description)
            
            if len(present_security_headers) >= 3:
                points = 4
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': f'Strong security headers present ({len(present_security_headers)}/4)',
                    'points': points,
                    'evidence': f'Headers: {", ".join(present_security_headers)}'
                })
            elif len(present_security_headers) >= 1:
                points = 2
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': f'Some security headers present ({len(present_security_headers)}/4)',
                    'points': points,
                    'evidence': f'Headers: {", ".join(present_security_headers)}'
                })
            else:
                points = -3
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': 'Missing security headers',
                    'points': abs(points),
                    'evidence': 'No security headers detected'
                })
            
            # Check server header
            server = headers.get('Server', '')
            if server:
                # Check for suspicious server signatures
                suspicious_servers = ['nginx/1.0', 'Apache/1.0', 'IIS/1.0']
                if any(susp in server for susp in suspicious_servers):
                    points = -2
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Suspicious server signature: {server}',
                        'points': abs(points),
                        'evidence': 'Old or fake server version'
                    })
            
        except Exception as e:
            logger.debug(f"Response header analysis failed: {e}")
    
    def _analyze_redirect(self, original_url: str, redirect_url: str, results: Dict):
        """Analyze redirect patterns"""
        
        try:
            original_domain = urlparse(original_url).netloc
            redirect_domain = urlparse(redirect_url).netloc
            
            if original_domain != redirect_domain:
                points = -6
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Redirects to different domain: {redirect_domain}',
                    'points': abs(points),
                    'evidence': f'Original: {original_domain} → Redirect: {redirect_domain}'
                })
            
            # Check for suspicious redirect patterns
            if 'bit.ly' in redirect_url or 'tinyurl' in redirect_url:
                points = -8
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': 'Redirects through URL shortener',
                    'points': abs(points),
                    'evidence': f'Redirect URL: {redirect_url}'
                })
                
        except Exception as e:
            logger.debug(f"Redirect analysis failed: {e}")

if __name__ == "__main__":
    # Test the technical analyzer
    analyzer = TechnicalAnalyzer()
    
    test_urls = [
        "https://www.google.com",
        "https://httpbin.org"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing technical aspects: {url}")
        result = analyzer.analyze_technical(url)
        if 'error' not in result:
            print(f"Score: {result['score']}")
            for explanation in result['explanations']:
                print(f"- {explanation['description']} ({explanation.get('points', 0)} points)")
        else:
            print(f"Error: {result['error']}")