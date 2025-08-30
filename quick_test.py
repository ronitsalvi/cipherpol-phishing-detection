"""
Quick test of the full phishing detection system
"""

from modules.phishing_detector import PhishingDetector
import time

def test_real_urls():
    """Test with real URLs"""
    
    print("🛡️ Testing Phishing Detection System")
    print("=" * 50)
    
    detector = PhishingDetector()
    
    # Test URLs - mix of legitimate and potentially suspicious patterns
    test_urls = [
        "https://www.google.com",
        "https://github.com",
        "https://httpbin.org"
    ]
    
    for url in test_urls:
        print(f"\n🔍 Analyzing: {url}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            result = detector.analyze_url(url)
            
            print(f"✅ Trust Score: {result['trust_score']}/100")
            print(f"🎯 Risk Level: {result['risk_level']}")
            print(f"🔮 Confidence: {result['confidence']}%")
            print(f"⏱️  Analysis Time: {result['analysis_time']:.2f}s")
            
            # Show component scores
            print(f"\n📊 Component Scores:")
            for component, score in result['component_scores'].items():
                print(f"   {component.title()}: {score}")
            
            # Show explanations
            explanations = result['explanations']
            
            if explanations.get('negative_signals'):
                print(f"\n❌ Top Risk Factors:")
                for signal in explanations['negative_signals'][:3]:
                    print(f"   • {signal['description']} (-{signal.get('points', 0)} pts)")
            
            if explanations.get('positive_signals'):
                print(f"\n✅ Positive Indicators:")
                for signal in explanations['positive_signals'][:3]:
                    print(f"   • {signal['description']} (+{signal.get('points', 0)} pts)")
            
            print(f"\n💡 Recommendation: {detector.get_recommendation(result)}")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")

def main():
    test_real_urls()

if __name__ == "__main__":
    main()