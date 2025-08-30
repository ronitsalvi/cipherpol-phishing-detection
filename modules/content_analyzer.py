"""
Content Analyzer Module
Analyzes web page content for phishing detection
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import textstat
from typing import Dict, List, Optional
import logging
from spellchecker import SpellChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analyzes web page content for phishing indicators"""
    
    def __init__(self):
        # Suspicious keywords that indicate phishing attempts
        self.urgent_keywords = {
            'urgent', 'immediate', 'act now', 'limited time', 'expires today',
            'expires soon', 'final notice', 'last chance', 'time sensitive',
            'immediate action', 'act immediately', 'expires in', 'hurry',
            'don\'t delay', 'act fast', 'time running out'
        }
        
        self.financial_keywords = {
            'verify account', 'confirm identity', 'update payment', 'suspended account',
            'account locked', 'security alert', 'unauthorized access', 'click here to verify',
            'confirm your account', 'update your information', 'verify your identity',
            'account verification', 'payment failed', 'billing problem', 'refund',
            'tax refund', 'prize money', 'lottery', 'winner', 'congratulations'
        }
        
        self.threat_keywords = {
            'account will be closed', 'account terminated', 'account suspended',
            'legal action', 'court order', 'arrest warrant', 'investigation',
            'criminal charges', 'fraud investigation', 'security breach'
        }
        
        self.social_engineering = {
            'click here', 'download now', 'install now', 'update required',
            'security update', 'important update', 'critical update',
            'verify now', 'confirm now', 'login here', 'sign in here'
        }
        
        # Brand names commonly impersonated
        self.common_brands = {
            'paypal', 'amazon', 'apple', 'microsoft', 'google', 'facebook',
            'instagram', 'twitter', 'linkedin', 'netflix', 'spotify',
            'ebay', 'alibaba', 'chase', 'bank of america', 'wells fargo',
            'citibank', 'american express', 'visa', 'mastercard'
        }
        
        self.spell_checker = SpellChecker()
    
    def analyze_content(self, url: str) -> Dict:
        """Perform comprehensive content analysis"""
        
        try:
            # Fetch webpage content
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = {
                'url': url,
                'score': 0,
                'explanations': []
            }
            
            # Extract text content
            page_text = soup.get_text()
            
            # Analyze different content aspects
            self._analyze_suspicious_keywords(page_text, results)
            self._analyze_forms(soup, url, results)
            self._analyze_links(soup, url, results)
            self._analyze_content_quality(page_text, results)
            self._analyze_brand_impersonation(page_text, soup, results)
            self._analyze_page_structure(soup, results)
            
            return results
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch content for {url}: {e}")
            return {'error': f'Failed to fetch content: {str(e)}'}
        except Exception as e:
            logger.error(f"Content analysis failed for {url}: {e}")
            return {'error': str(e)}
    
    def _analyze_suspicious_keywords(self, text: str, results: Dict):
        """Analyze text for suspicious keywords and phrases"""
        
        text_lower = text.lower()
        found_urgent = []
        found_financial = []
        found_threats = []
        found_social_eng = []
        
        # Check for urgent keywords
        for keyword in self.urgent_keywords:
            if keyword in text_lower:
                found_urgent.append(keyword)
        
        # Check for financial keywords
        for keyword in self.financial_keywords:
            if keyword in text_lower:
                found_financial.append(keyword)
        
        # Check for threat keywords
        for keyword in self.threat_keywords:
            if keyword in text_lower:
                found_threats.append(keyword)
        
        # Check for social engineering keywords
        for keyword in self.social_engineering:
            if keyword in text_lower:
                found_social_eng.append(keyword)
        
        # Score based on findings
        total_suspicious = len(found_urgent) + len(found_financial) + len(found_threats) + len(found_social_eng)
        
        if found_threats:
            points = -15
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains threatening language: {", ".join(found_threats[:3])}',
                'points': abs(points),
                'evidence': f'Found {len(found_threats)} threat-related phrases'
            })
        
        if found_urgent:
            points = -10 if len(found_urgent) > 2 else -5
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains urgent language: {", ".join(found_urgent[:3])}',
                'points': abs(points),
                'evidence': f'Found {len(found_urgent)} urgency phrases'
            })
        
        if found_financial:
            points = -10 if len(found_financial) > 2 else -6
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains financial/verification language: {", ".join(found_financial[:3])}',
                'points': abs(points),
                'evidence': f'Found {len(found_financial)} financial phrases'
            })
        
        if found_social_eng:
            points = -8 if len(found_social_eng) > 2 else -4
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains social engineering language: {", ".join(found_social_eng[:3])}',
                'points': abs(points),
                'evidence': f'Found {len(found_social_eng)} social engineering phrases'
            })
        
        if total_suspicious == 0:
            points = 3
            results['score'] += points
            results['explanations'].append({
                'type': 'positive',
                'description': 'No suspicious keywords detected',
                'points': points,
                'evidence': 'Clean content language'
            })
    
    def _analyze_forms(self, soup: BeautifulSoup, url: str, results: Dict):
        """Analyze forms for security issues"""
        
        forms = soup.find_all('form')
        
        if not forms:
            results['explanations'].append({
                'type': 'neutral',
                'description': 'No forms detected on page',
                'evidence': 'Form count: 0'
            })
            return
        
        # Check each form
        insecure_forms = 0
        login_forms = 0
        
        for form in forms:
            # Check if form is over HTTP instead of HTTPS
            action = form.get('action', '')
            if action.startswith('http://'):
                insecure_forms += 1
            
            # Check for login-related inputs
            inputs = form.find_all('input')
            has_password = any(inp.get('type') == 'password' for inp in inputs)
            has_email_or_user = any(
                inp.get('type') in ['email', 'text'] and 
                inp.get('name', '').lower() in ['email', 'username', 'user', 'login']
                for inp in inputs
            )
            
            if has_password or (has_email_or_user and has_password):
                login_forms += 1
        
        # Score based on form security
        if insecure_forms > 0:
            points = -15
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Forms submit over insecure HTTP ({insecure_forms} forms)',
                'points': abs(points),
                'evidence': 'Forms not using HTTPS encryption'
            })
        
        if login_forms > 0 and not url.startswith('https://'):
            points = -12
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Login form on non-HTTPS page ({login_forms} forms)',
                'points': abs(points),
                'evidence': 'Password forms without encryption'
            })
        elif login_forms > 0:
            results['explanations'].append({
                'type': 'neutral',
                'description': f'Login forms detected ({login_forms} forms)',
                'evidence': 'Forms properly secured with HTTPS'
            })
    
    def _analyze_links(self, soup: BeautifulSoup, url: str, results: Dict):
        """Analyze link patterns for suspicious behavior"""
        
        links = soup.find_all('a', href=True)
        
        if not links:
            results['explanations'].append({
                'type': 'neutral',
                'description': 'No links detected on page',
                'evidence': 'Link count: 0'
            })
            return
        
        external_links = 0
        suspicious_links = 0
        redirect_links = 0
        
        parsed_base = urlparse(url)
        base_domain = parsed_base.netloc
        
        for link in links:
            href = link.get('href', '')
            
            # Skip empty links and anchors
            if not href or href.startswith('#'):
                continue
            
            # Check for external links
            if href.startswith('http'):
                parsed_link = urlparse(href)
                if parsed_link.netloc != base_domain:
                    external_links += 1
                    
                    # Check for suspicious redirect patterns
                    if 'redirect' in href.lower() or 'r?url=' in href.lower():
                        redirect_links += 1
                    
                    # Check for URL shorteners (suspicious in phishing)
                    shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly']
                    if any(shortener in parsed_link.netloc for shortener in shorteners):
                        suspicious_links += 1
        
        total_links = len(links)
        external_ratio = external_links / total_links if total_links > 0 else 0
        
        # Score based on link analysis
        if external_ratio > 0.7:  # More than 70% external links
            points = -8
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'High proportion of external links ({external_ratio:.1%})',
                'points': abs(points),
                'evidence': f'{external_links}/{total_links} links are external'
            })
        
        if redirect_links > 0:
            points = -6
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains redirect links ({redirect_links} links)',
                'points': abs(points),
                'evidence': 'Redirect patterns detected'
            })
        
        if suspicious_links > 0:
            points = -10
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Contains URL shortener links ({suspicious_links} links)',
                'points': abs(points),
                'evidence': 'URL shorteners often used in phishing'
            })
    
    def _analyze_content_quality(self, text: str, results: Dict):
        """Analyze content quality indicators"""
        
        if len(text.strip()) < 100:
            points = -5
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'Very little content on page',
                'points': abs(points),
                'evidence': f'Text length: {len(text.strip())} characters'
            })
            return
        
        # Basic readability analysis
        try:
            readability_score = textstat.flesch_reading_ease(text)
            
            if readability_score < 30:  # Very difficult to read
                points = -4
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': 'Content is very difficult to read',
                    'points': abs(points),
                    'evidence': f'Readability score: {readability_score:.1f}'
                })
            elif readability_score > 80:  # Very easy to read (potentially oversimplified)
                results['explanations'].append({
                    'type': 'neutral',
                    'description': 'Content is very easy to read',
                    'evidence': f'Readability score: {readability_score:.1f}'
                })
        except:
            pass
        
        # Spell checking (sample of text)
        words = text.split()[:100]  # Check first 100 words
        misspelled = self.spell_checker.unknown(words)
        
        if len(misspelled) > len(words) * 0.05:  # More than 5% misspelled
            points = -6
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': f'Poor spelling quality ({len(misspelled)} errors in sample)',
                'points': abs(points),
                'evidence': f'Misspelled words found: {len(misspelled)}/{len(words)}'
            })
    
    def _analyze_brand_impersonation(self, text: str, soup: BeautifulSoup, results: Dict):
        """Analyze for brand impersonation attempts"""
        
        text_lower = text.lower()
        found_brands = []
        
        # Check for brand mentions in text
        for brand in self.common_brands:
            if brand in text_lower:
                found_brands.append(brand)
        
        if found_brands:
            # Check if page title or domain matches the brand
            title = soup.find('title')
            title_text = title.text.lower() if title else ''
            
            domain = urlparse(results['url']).netloc.lower()
            
            suspicious_branding = []
            
            for brand in found_brands:
                # If brand is mentioned but not in domain or title, suspicious
                if brand not in domain and brand not in title_text:
                    suspicious_branding.append(brand)
            
            if suspicious_branding:
                points = -12
                results['score'] += points
                results['explanations'].append({
                    'type': 'negative',
                    'description': f'Mentions brands not matching domain: {", ".join(suspicious_branding[:3])}',
                    'points': abs(points),
                    'evidence': f'Brand mentions without legitimate association'
                })
            else:
                results['explanations'].append({
                    'type': 'neutral',
                    'description': f'Brand mentions appear legitimate: {", ".join(found_brands[:3])}',
                    'evidence': 'Brands mentioned match domain/title'
                })
    
    def _analyze_page_structure(self, soup: BeautifulSoup, results: Dict):
        """Analyze page structure for legitimacy indicators"""
        
        # Check for common legitimate page elements
        has_nav = bool(soup.find('nav') or soup.find('div', class_=re.compile(r'nav')))
        has_footer = bool(soup.find('footer') or soup.find('div', class_=re.compile(r'footer')))
        has_header = bool(soup.find('header') or soup.find('div', class_=re.compile(r'header')))
        
        legitimate_elements = sum([has_nav, has_footer, has_header])
        
        if legitimate_elements >= 2:
            points = 5
            results['score'] += points
            results['explanations'].append({
                'type': 'positive',
                'description': 'Page has proper structure (header, nav, footer)',
                'points': points,
                'evidence': f'{legitimate_elements}/3 structural elements present'
            })
        elif legitimate_elements == 0:
            points = -4
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'Page lacks basic structure elements',
                'points': abs(points),
                'evidence': 'No header, navigation, or footer detected'
            })
        
        # Check for contact information
        contact_indicators = [
            'contact', 'phone', 'email', 'address', 'about us',
            'privacy policy', 'terms of service', 'support'
        ]
        
        page_text = soup.get_text().lower()
        contact_elements = sum(1 for indicator in contact_indicators if indicator in page_text)
        
        if contact_elements >= 3:
            points = 3
            results['score'] += points
            results['explanations'].append({
                'type': 'positive',
                'description': 'Page contains contact and policy information',
                'points': points,
                'evidence': f'{contact_elements}/8 contact indicators found'
            })
        elif contact_elements == 0:
            points = -3
            results['score'] += points
            results['explanations'].append({
                'type': 'negative',
                'description': 'Page lacks contact and policy information',
                'points': abs(points),
                'evidence': 'No contact/policy information found'
            })

if __name__ == "__main__":
    # Test the content analyzer
    analyzer = ContentAnalyzer()
    
    test_urls = [
        "https://www.google.com",
        "https://httpbin.org/html"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing content: {url}")
        result = analyzer.analyze_content(url)
        if 'error' not in result:
            print(f"Score: {result['score']}")
            for explanation in result['explanations']:
                print(f"- {explanation['description']} ({explanation.get('points', 0)} points)")
        else:
            print(f"Error: {result['error']}")