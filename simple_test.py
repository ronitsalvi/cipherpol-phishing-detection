"""
Simple test script to verify core functionality without all dependencies
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_basic_imports():
    """Test if basic modules can be imported"""
    
    print("🔧 Testing Basic Imports")
    print("=" * 30)
    
    try:
        from modules.domain_analyzer import DomainAnalyzer
        print("✅ Domain Analyzer imported successfully")
    except Exception as e:
        print(f"❌ Domain Analyzer import failed: {e}")
    
    try:
        from modules.content_analyzer import ContentAnalyzer
        print("✅ Content Analyzer imported successfully")
    except Exception as e:
        print(f"❌ Content Analyzer import failed: {e}")
    
    try:
        from modules.technical_analyzer import TechnicalAnalyzer
        print("✅ Technical Analyzer imported successfully")
    except Exception as e:
        print(f"❌ Technical Analyzer import failed: {e}")
    
    try:
        from modules.phishing_detector import PhishingDetector
        print("✅ Phishing Detector imported successfully")
    except Exception as e:
        print(f"❌ Phishing Detector import failed: {e}")

def test_url_parsing():
    """Test basic URL parsing functionality"""
    
    print("\n🌐 Testing URL Parsing")
    print("=" * 30)
    
    from urllib.parse import urlparse
    
    test_urls = [
        "https://www.google.com",
        "http://suspicious-site.tk",
        "https://secure-bank-login.ml"
    ]
    
    for url in test_urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            print(f"✅ {url} → {domain}")
        except Exception as e:
            print(f"❌ Failed to parse {url}: {e}")

def test_basic_domain_analysis():
    """Test domain analysis without external dependencies"""
    
    print("\n🔍 Testing Basic Domain Analysis")
    print("=" * 40)
    
    # Simple domain characteristic tests
    test_domains = [
        "google.com",
        "very-long-suspicious-domain-name-here.tk", 
        "secure-bank-login123.ml",
        "github.com"
    ]
    
    for domain in test_domains:
        print(f"\nAnalyzing: {domain}")
        
        # Length test
        length_score = -10 if len(domain) > 30 else (-5 if len(domain) > 20 else 0)
        print(f"  Length: {len(domain)} chars → {length_score} points")
        
        # TLD test
        high_risk_tlds = {'tk', 'ml', 'ga', 'cf', 'pw', 'cc'}
        tld = domain.split('.')[-1]
        tld_score = -15 if tld in high_risk_tlds else (5 if tld in ['com', 'org', 'net'] else 0)
        print(f"  TLD: .{tld} → {tld_score} points")
        
        # Character analysis
        hyphen_count = domain.count('-')
        digit_count = sum(c.isdigit() for c in domain)
        char_score = (-8 if hyphen_count > 2 else 0) + (-6 if digit_count > 3 else 0)
        print(f"  Characters: {hyphen_count} hyphens, {digit_count} digits → {char_score} points")
        
        total = 70 + length_score + tld_score + char_score  # Base score of 70
        print(f"  🎯 Estimated Trust Score: {max(0, min(100, total))}/100")

def test_content_keywords():
    """Test content keyword analysis"""
    
    print("\n📝 Testing Content Keyword Analysis")
    print("=" * 40)
    
    test_texts = [
        "Welcome to our legitimate business website. Contact us for support.",
        "URGENT! Your account will be suspended! Click here to verify now!",
        "Limited time offer! Act now before it expires! Verify your account immediately!"
    ]
    
    urgent_keywords = ['urgent', 'immediate', 'act now', 'limited time', 'expires', 'suspended']
    financial_keywords = ['verify account', 'confirm identity', 'click here to verify', 'account suspended']
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nText {i}: {text[:50]}...")
        
        text_lower = text.lower()
        urgent_found = [kw for kw in urgent_keywords if kw in text_lower]
        financial_found = [kw for kw in financial_keywords if kw in text_lower]
        
        urgent_score = -10 if len(urgent_found) > 2 else (-5 if urgent_found else 0)
        financial_score = -10 if len(financial_found) > 2 else (-6 if financial_found else 0)
        
        print(f"  Urgent keywords: {urgent_found} → {urgent_score} points")
        print(f"  Financial keywords: {financial_found} → {financial_score} points")
        
        content_score = 70 + urgent_score + financial_score
        print(f"  🎯 Content Trust Score: {max(0, min(100, content_score))}/100")

def main():
    """Run simple tests"""
    
    print("🧪 Simple Phishing Detection Test Suite")
    print("=" * 50)
    print("Testing core functionality without full dependencies\n")
    
    test_basic_imports()
    test_url_parsing()
    test_basic_domain_analysis()
    test_content_keywords()
    
    print("\n🎉 Simple tests completed!")
    print("\n💡 Next Steps:")
    print("   1. Install remaining dependencies with 'pip3 install -r requirements.txt'")
    print("   2. Run full test suite with 'python3 test_system.py'")
    print("   3. Start Streamlit app with 'streamlit run app.py'")

if __name__ == "__main__":
    main()