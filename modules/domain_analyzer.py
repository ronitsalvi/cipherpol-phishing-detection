"""
Domain Analyzer Module
Analyzes domain characteristics for phishing detection
"""

import dns.resolver
import dns.exception
import whois
import re
import socket
import ssl
import datetime
import math
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from collections import Counter
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainAnalyzer:
    """Analyzes domain-related features for phishing detection"""
    
    def __init__(self):
        # High-risk TLDs commonly used for phishing
        self.high_risk_tlds = {
            'tk', 'ml', 'ga', 'cf', 'pw', 'cc', 'info', 'biz', 'mobi', 'name',
            'pro', 'travel', 'xxx', 'click', 'download', 'stream', 'racing',
            'cricket', 'science', 'work', 'party', 'gq', 'men', 'win', 'date'
        }
        
        # Suspicious keywords in domains
        self.suspicious_keywords = {
            'secure', 'bank', 'paypal', 'amazon', 'microsoft', 'google', 'apple',
            'facebook', 'login', 'signin', 'verify', 'update', 'suspended',
            'security', 'alert', 'warning', 'urgent', 'confirm', 'validation'
        }
        
        # Legitimate TLDs that are generally trusted
        self.trusted_tlds = {
            'com', 'org', 'net', 'edu', 'gov', 'mil', 'int', 'co.uk', 'de',
            'fr', 'it', 'es', 'nl', 'au', 'ca', 'jp', 'kr'
        }
        
        # Advanced detection patterns
        self.ip_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
        
        # Major brands for typosquatting detection
        self.major_brands = {
            'google.com', 'facebook.com', 'paypal.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'spotify.com', 'instagram.com', 'twitter.com',
            'linkedin.com', 'ebay.com', 'chase.com', 'bankofamerica.com', 'wells-fargo.com'
        }
    
    def analyze_domain(self, url: str) -> Dict:
        """Perform comprehensive domain analysis"""
        
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
            
            # Analyze different domain aspects
            self._analyze_domain_structure(domain, results)
            self._analyze_tld_risk(domain, results)  
            self._analyze_domain_age(domain, results)
            self._analyze_subdomain_patterns(parsed_url, results)
            self._analyze_ssl_certificate(domain, results)
            self._analyze_dns_records(domain, results)
            
            # Advanced detection features
            self._detect_ip_in_domain(domain, results)
            self._detect_typosquatting(domain, results)
            self._detect_homograph_attacks(domain, results)
            self._analyze_domain_entropy(domain, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Domain analysis failed for {url}: {e}")
            return {'error': str(e)}
    
    def _analyze_domain_structure(self, domain: str, results: Dict):
        """Analyze domain string characteristics"""
        
        # Domain length analysis
        if len(domain) > 30:
            points = -10
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Very long domain name ({len(domain)} characters)',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
        elif len(domain) > 20:
            points = -5
            results['score'] += points
            results['explanations'].append({
                'type': 'negative', 
                'description': f'Long domain name ({len(domain)} characters)',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
        
        # Character composition analysis
        hyphen_count = domain.count('-')
        digit_count = sum(c.isdigit() for c in domain)
        
        if hyphen_count > 2:
            points = -8
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Multiple hyphens in domain ({hyphen_count} hyphens)',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
        elif hyphen_count > 0:
            points = -3
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains hyphens ({hyphen_count} hyphen{"s" if hyphen_count > 1 else ""})',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
        
        if digit_count > 3:
            points = -6
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Many digits in domain ({digit_count} digits)',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
        
        # Suspicious keyword analysis
        domain_lower = domain.lower()
        found_keywords = []
        
        for keyword in self.suspicious_keywords:
            if keyword in domain_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            points = -10 if len(found_keywords) > 1 else -5
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains suspicious keywords: {", ".join(found_keywords)}',
                'points': abs(points),
                'evidence': f'Domain: {domain}'
            })
    
    def _analyze_tld_risk(self, domain: str, results: Dict):
        """Analyze top-level domain risk"""
        
        try:
            # Extract TLD
            parts = domain.split('.')
            if len(parts) < 2:
                return
                
            tld = parts[-1].lower()
            
            # Check for multi-part TLD (like co.uk)
            if len(parts) >= 3 and f"{parts[-2]}.{parts[-1]}" in self.trusted_tlds:
                tld = f"{parts[-2]}.{parts[-1]}"
            
            if tld in self.high_risk_tlds:
                points = -15
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Uses high-risk TLD (.{tld})',
                    'points': abs(points),
                    'evidence': f'TLD: .{tld}'
                })
            elif tld in self.trusted_tlds:
                points = 5
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': f'Uses trusted TLD (.{tld})',
                    'points': points,
                    'evidence': f'TLD: .{tld}'
                })
            else:
                results['explanations'].append({
                    'type': 'neutral',
                    'description': f'Uses uncommon TLD (.{tld})',
                    'evidence': f'TLD: .{tld}'
                })
                
        except Exception as e:
            logger.debug(f"TLD analysis failed: {e}")
    
    def _analyze_domain_age(self, domain: str, results: Dict):
        """Analyze domain registration age"""
        
        try:
            # Attempt to get WHOIS information
            domain_info = whois.whois(domain)
            
            if domain_info and domain_info.creation_date:
                creation_date = domain_info.creation_date
                
                # Handle list of dates (some whois returns multiple)
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]
                
                # Calculate domain age
                now = datetime.datetime.now()
                if creation_date.tzinfo:
                    now = now.replace(tzinfo=creation_date.tzinfo)
                
                age_days = (now - creation_date).days
                age_months = age_days / 30.44
                
                if age_days < 30:  # Less than 1 month
                    points = -15
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Very recently registered domain ({age_days} days ago)',
                        'points': abs(points),
                        'evidence': f'Created: {creation_date.strftime("%Y-%m-%d")}'
                    })
                elif age_days < 90:  # Less than 3 months
                    points = -10
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Recently registered domain ({int(age_months)} months ago)',
                        'points': abs(points),
                        'evidence': f'Created: {creation_date.strftime("%Y-%m-%d")}'
                    })
                elif age_days < 365:  # Less than 1 year
                    points = -5
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Relatively new domain ({int(age_months)} months old)',
                        'points': abs(points),
                        'evidence': f'Created: {creation_date.strftime("%Y-%m-%d")}'
                    })
                elif age_days > 365 * 5:  # More than 5 years
                    points = 10
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': f'Well-established domain ({int(age_days/365)} years old)',
                        'points': points,
                        'evidence': f'Created: {creation_date.strftime("%Y-%m-%d")}'
                    })
                else:
                    results['explanations'].append({
                        'type': 'neutral',
                        'description': f'Domain age: {int(age_months)} months',
                        'evidence': f'Created: {creation_date.strftime("%Y-%m-%d")}'
                    })
                    
        except Exception as e:
            logger.debug(f"Domain age analysis failed for {domain}: {e}")
            results['explanations'].append({
                'type': 'neutral',
                'description': 'Domain age information unavailable',
                'evidence': 'WHOIS lookup failed'
            })
    
    def _analyze_subdomain_patterns(self, parsed_url, results: Dict):
        """Analyze subdomain patterns for suspicious activity"""
        
        try:
            hostname = parsed_url.netloc
            parts = hostname.split('.')
            
            # Count subdomains (excluding main domain and TLD)
            if len(parts) > 2:
                subdomain_count = len(parts) - 2
                subdomains = '.'.join(parts[:-2])
                
                if subdomain_count > 3:
                    points = -10
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Many subdomain levels ({subdomain_count} levels)',
                        'points': abs(points),
                        'evidence': f'Subdomains: {subdomains}'
                    })
                elif subdomain_count > 1:
                    # Check if subdomains look suspicious
                    suspicious_subdomains = []
                    for subdomain in parts[:-2]:
                        if any(keyword in subdomain.lower() for keyword in self.suspicious_keywords):
                            suspicious_subdomains.append(subdomain)
                    
                    if suspicious_subdomains:
                        points = -8
                        results['score'] += points
                        results['explanations'].append({
                            'type': 'negative',
                            'description': f'Suspicious subdomains detected: {", ".join(suspicious_subdomains)}',
                            'points': abs(points),
                            'evidence': f'Full hostname: {hostname}'
                        })
                
                # Check for common legitimate subdomains
                common_legitimate = {'www', 'mail', 'ftp', 'blog', 'shop', 'store', 'support', 'help', 'api'}
                if len(parts) == 3 and parts[0].lower() in common_legitimate:
                    results['explanations'].append({
                        'type': 'neutral',
                        'description': f'Common subdomain pattern: {parts[0]}',
                        'evidence': f'Subdomain: {parts[0]}'
                    })
                    
        except Exception as e:
            logger.debug(f"Subdomain analysis failed: {e}")
    
    def _analyze_ssl_certificate(self, domain: str, results: Dict):
        """Analyze SSL certificate characteristics"""
        
        try:
            # Try to get SSL certificate info
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Certificate exists (minimal bonus - SSL is standard now)
                    points = 2
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': 'SSL certificate present',
                        'points': points,
                        'evidence': f'Issued to: {cert.get("subject", "Unknown")}'
                    })
                    
                    # Check certificate age
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry_date = datetime.datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.datetime.now()).days
                        
                        if days_until_expiry < 30:
                            points = -5
                            results['score'] += points
                            results['explanations'].append({
                                'type': 'negative',
                                'description': f'SSL certificate expires soon ({days_until_expiry} days)',
                                'points': abs(points),
                                'evidence': f'Expires: {expiry_date.strftime("%Y-%m-%d")}'
                            })
                    
        except (socket.timeout, socket.gaierror, ssl.SSLError, ConnectionRefusedError):
            points = -10
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'No SSL certificate or connection failed',
                'points': abs(points),
                'evidence': 'SSL handshake failed'
            })
        except Exception as e:
            logger.debug(f"SSL analysis failed for {domain}: {e}")
    
    def _analyze_dns_records(self, domain: str, results: Dict):
        """Analyze DNS record patterns"""
        
        try:
            # Check for basic DNS records
            has_mx = False
            has_a = False
            
            try:
                dns.resolver.resolve(domain, 'A')
                has_a = True
            except:
                pass
                
            try:
                dns.resolver.resolve(domain, 'MX')
                has_mx = True
            except:
                pass
            
            if has_a and has_mx:
                points = 3
                results['score'] += points
                results['explanations'].append({
                    'type': 'positive',
                    'description': 'Complete DNS record set (A and MX records)',
                    'points': points,
                    'evidence': 'DNS records properly configured'
                })
            elif has_a:
                results['explanations'].append({
                    'type': 'neutral',
                    'description': 'Basic DNS records present',
                    'evidence': 'Has A record but no MX record'
                })
            else:
                points = -8
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': 'Missing basic DNS records',
                    'points': abs(points),
                    'evidence': 'DNS resolution issues'
                })
                
        except Exception as e:
            logger.debug(f"DNS analysis failed for {domain}: {e}")
    
    def _detect_ip_in_domain(self, domain: str, results: Dict):
        """Detect if URL uses IP address instead of domain name"""
        
        try:
            # Remove port if present
            domain_part = domain.split(':')[0]
            
            # Check if domain is an IP address
            if self.ip_pattern.match(domain_part):
                points = -20
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Uses IP address instead of domain name',
                    'points': abs(points),
                    'evidence': f'IP address: {domain_part}'
                })
                
        except Exception as e:
            logger.debug(f"IP detection failed for {domain}: {e}")
    
    def _detect_typosquatting(self, domain: str, results: Dict):
        """Detect typosquatting attempts against major brands"""
        
        try:
            domain_lower = domain.lower()
            
            # Remove common subdomains for analysis
            if domain_lower.startswith('www.'):
                domain_lower = domain_lower[4:]
            
            # Check similarity against major brands
            for brand_domain in self.major_brands:
                ratio = SequenceMatcher(None, domain_lower, brand_domain).ratio()
                
                # Sweet spot: similar enough to be suspicious but not identical
                if 0.85 < ratio < 0.995 and domain_lower != brand_domain:
                    points = -15
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Possible typosquatting of {brand_domain}',
                        'points': abs(points),
                        'evidence': f'Similarity ratio: {ratio:.3f} to {brand_domain}'
                    })
                    break  # Only flag once per domain
                    
        except Exception as e:
            logger.debug(f"Typosquatting detection failed for {domain}: {e}")
    
    def _detect_homograph_attacks(self, domain: str, results: Dict):
        """Detect Unicode homograph attacks"""
        
        try:
            # Check if domain can be encoded as ASCII
            try:
                domain.encode('ascii')
                # If we get here, domain is pure ASCII - no homograph attack
            except UnicodeEncodeError:
                # Domain contains non-ASCII characters - potential homograph attack
                points = -18
                results['score'] += points
                
                # Analyze which characters are suspicious
                suspicious_chars = []
                for char in domain:
                    if ord(char) > 127:  # Non-ASCII character
                        suspicious_chars.append(f"{char}(U+{ord(char):04X})")
                
                results['explanations'].append({
                    'type': 'negative',
                    'description': 'Possible homograph attack (Unicode characters)',
                    'points': abs(points),
                    'evidence': f'Non-ASCII characters: {", ".join(suspicious_chars[:5])}'
                })
                
        except Exception as e:
            logger.debug(f"Homograph detection failed for {domain}: {e}")
    
    def _analyze_domain_entropy(self, domain: str, results: Dict):
        """Analyze domain randomness using entropy calculation"""
        
        try:
            # Extract the main domain label (before first dot)
            domain_parts = domain.split('.')
            if len(domain_parts) < 2:
                return
                
            main_label = domain_parts[0]
            
            # Remove common prefixes
            if main_label.startswith('www'):
                main_label = main_label[3:]
            
            if len(main_label) < 4:  # Too short for meaningful entropy analysis
                return
            
            # Calculate Shannon entropy
            frequency = Counter(main_label.lower())
            length = len(main_label)
            
            if length == 0:
                return
            
            entropy = 0
            for count in frequency.values():
                prob = count / length
                entropy -= prob * math.log2(prob)
            
            # High entropy with reasonable length suggests randomized domain
            if entropy > 3.8 and length >= 8:
                points = -12
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Highly randomized domain name detected',
                    'points': abs(points),
                    'evidence': f'Shannon entropy: {entropy:.2f} (threshold: 3.8)'
                })
            
            # Also check consonant/vowel ratio for additional randomness indicators
            vowels = 'aeiou'
            vowel_count = sum(1 for c in main_label.lower() if c in vowels)
            consonant_count = sum(1 for c in main_label.lower() if c.isalpha() and c not in vowels)
            
            if vowel_count > 0:
                cv_ratio = consonant_count / vowel_count
                if (cv_ratio > 4 or cv_ratio < 0.3) and length >= 6:
                    points = -6
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Unusual letter distribution in domain',
                        'points': abs(points),
                        'evidence': f'Consonant/vowel ratio: {cv_ratio:.2f} (unusual)'
                    })
            
        except Exception as e:
            logger.debug(f"Domain entropy analysis failed for {domain}: {e}")

if __name__ == "__main__":
    # Test the domain analyzer
    analyzer = DomainAnalyzer()
    
    test_urls = [
        "https://www.google.com",
        "https://secure-bank-login.tk",
        "https://paypal-verify-account.ml"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing: {url}")
        result = analyzer.analyze_domain(url)
        print(f"Score: {result.get('score', 'Error')}")
        for explanation in result.get('explanations', []):
            print(f"- {explanation['description']} ({explanation.get('points', 0)} points)")