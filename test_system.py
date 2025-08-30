"""
Test Script for Phishing Detection System
Tests all components and generates sample analysis
"""

from modules.phishing_detector import PhishingDetector
from modules.data_loader import DataLoader
import time

def test_individual_modules():
    """Test each module individually"""
    
    print("🔧 Testing Individual Modules")
    print("="*50)
    
    # Test URLs
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "https://httpbin.org/html"
    ]
    
    detector = PhishingDetector()
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        
        # Test domain analyzer
        try:
            domain_result = detector.domain_analyzer.analyze_domain(url)
            print(f"  ✅ Domain Analysis: Score {domain_result.get('score', 'Error')}")
        except Exception as e:
            print(f"  ❌ Domain Analysis Failed: {e}")
        
        # Test content analyzer  
        try:
            content_result = detector.content_analyzer.analyze_content(url)
            print(f"  ✅ Content Analysis: Score {content_result.get('score', 'Error')}")
        except Exception as e:
            print(f"  ❌ Content Analysis Failed: {e}")
        
        # Test technical analyzer
        try:
            technical_result = detector.technical_analyzer.analyze_technical(url)
            print(f"  ✅ Technical Analysis: Score {technical_result.get('score', 'Error')}")
        except Exception as e:
            print(f"  ❌ Technical Analysis Failed: {e}")

def test_full_system():
    """Test the complete phishing detection system"""
    
    print("\n🛡️ Testing Complete Phishing Detection System")
    print("="*60)
    
    detector = PhishingDetector()
    
    # Test with a variety of URLs
    test_urls = [
        "https://www.google.com",
        "https://www.microsoft.com", 
        "https://github.com",
        "https://httpbin.org/html"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        print("-" * 40)
        
        start_time = time.time()
        result = detector.analyze_url(url)
        
        if 'error' not in str(result):
            print(f"✅ Trust Score: {result['trust_score']}/100")
            print(f"🎯 Risk Level: {result['risk_level']}")
            print(f"🔮 Confidence: {result['confidence']}%")
            print(f"⏱️  Analysis Time: {result['analysis_time']:.2f}s")
            
            # Show top explanations
            explanations = result['explanations']
            
            if explanations.get('negative_signals'):
                print(f"\n❌ Top Risk Factors:")
                for signal in explanations['negative_signals'][:3]:
                    print(f"   • {signal['description']} (-{signal.get('points', 0)} pts)")
            
            if explanations.get('positive_signals'):
                print(f"\n✅ Positive Indicators:")
                for signal in explanations['positive_signals'][:2]:
                    print(f"   • {signal['description']} (+{signal.get('points', 0)} pts)")
            
            print(f"\n💡 Recommendation: {detector.get_recommendation(result)}")
        else:
            print(f"❌ Analysis failed: {result}")

def test_data_loader():
    """Test data loading functionality"""
    
    print("\n📊 Testing Data Loader")
    print("="*30)
    
    loader = DataLoader()
    
    print("🔄 Testing legitimate URL generation...")
    try:
        legitimate_urls = loader.get_legitimate_urls(max_samples=50)
        print(f"✅ Generated {len(legitimate_urls)} legitimate URLs")
        print("Sample URLs:")
        for url in legitimate_urls['url'][:5]:
            print(f"   • {url}")
    except Exception as e:
        print(f"❌ Legitimate URL generation failed: {e}")
    
    print("\n🔄 Testing PhishTank data download (first 100 samples)...")
    try:
        phishing_urls = loader.download_phishtank_data(max_samples=100)
        print(f"✅ Downloaded {len(phishing_urls)} phishing URLs")
        if len(phishing_urls) > 0:
            print("Sample phishing URLs:")
            for url in phishing_urls['url'][:3]:
                print(f"   • {url}")
    except Exception as e:
        print(f"❌ PhishTank download failed: {e}")

def performance_test():
    """Test system performance"""
    
    print("\n⚡ Performance Testing")
    print("="*30)
    
    detector = PhishingDetector()
    
    # Test multiple URLs for average performance
    test_urls = [
        "https://www.google.com",
        "https://www.github.com", 
        "https://www.stackoverflow.com"
    ]
    
    total_time = 0
    successful_analyses = 0
    
    for url in test_urls:
        try:
            start_time = time.time()
            result = detector.analyze_url(url)
            end_time = time.time()
            
            analysis_time = end_time - start_time
            total_time += analysis_time
            successful_analyses += 1
            
            print(f"⏱️ {url}: {analysis_time:.2f}s")
            
        except Exception as e:
            print(f"❌ {url}: Failed ({e})")
    
    if successful_analyses > 0:
        avg_time = total_time / successful_analyses
        print(f"\n📈 Average Analysis Time: {avg_time:.2f} seconds")
        print(f"🎯 Target: < 30 seconds per URL")
        print(f"✅ Performance: {'GOOD' if avg_time < 30 else 'NEEDS OPTIMIZATION'}")
    
def main():
    """Run all tests"""
    
    print("🧪 Phishing Detection System - Comprehensive Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Individual modules
        test_individual_modules()
        
        # Test 2: Complete system
        test_full_system()
        
        # Test 3: Data loader
        test_data_loader()
        
        # Test 4: Performance
        performance_test()
        
        print("\n🎉 All tests completed!")
        print("\n💡 Next Steps:")
        print("   1. Run 'streamlit run app.py' to start the web interface")
        print("   2. Test with suspicious URLs to validate detection capabilities")
        print("   3. Review explanation quality and adjust scoring weights if needed")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        print("Check your internet connection and required dependencies")

if __name__ == "__main__":
    main()