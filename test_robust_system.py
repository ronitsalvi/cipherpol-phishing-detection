"""
Test the robust phishing detection system
Tests both simple and problematic URLs
"""

from modules.robust_phishing_detector import RobustPhishingDetector
import time

def test_robust_detector():
    """Test the robust detector with various URLs"""
    
    print("🧪 Testing Robust Phishing Detection System")
    print("=" * 60)
    
    detector = RobustPhishingDetector()
    
    # Test URLs including the problematic Instagram one
    test_urls = [
        ("Simple test", "https://www.google.com"),
        ("GitHub test", "https://github.com"),
        ("Instagram test (problematic)", "https://www.instagram.com/reel/DLfVr2_i7sM/?igsh=ZHRvc3owMnlvamlz"),
        ("Invalid URL test", "invalid-url"),
        ("Complex social media", "https://twitter.com/complex/status/123456789"),
    ]
    
    results = []
    
    for test_name, url in test_urls:
        print(f"\n🔍 {test_name}")
        print(f"URL: {url}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = detector.analyze_url(url)
            analysis_time = time.time() - start_time
            
            # Core results
            trust_score = result['trust_score']
            risk_level = result['risk_level']
            confidence = result['confidence']
            
            print(f"✅ Result: {trust_score}/100 - {risk_level}")
            print(f"🔮 Confidence: {confidence}%")
            print(f"⏱️  Time: {analysis_time:.2f}s")
            
            # Analysis status
            analysis_status = result.get('analysis_status', {})
            if analysis_status.get('partial_analysis'):
                successful = analysis_status.get('successful_modules', 0)
                total = analysis_status.get('total_modules', 3)
                print(f"⚠️  Partial: {successful}/{total} modules successful")
            
            # Component scores
            component_scores = result['component_scores']
            print(f"📊 Components: D:{component_scores['domain']} C:{component_scores['content']} T:{component_scores['technical']}")
            
            # Recommendation
            recommendation = detector.get_recommendation(result)
            print(f"💡 {recommendation}")
            
            results.append({
                'test': test_name,
                'url': url,
                'success': True,
                'trust_score': trust_score,
                'time': analysis_time
            })
            
        except Exception as e:
            print(f"❌ SYSTEM ERROR: {e}")
            results.append({
                'test': test_name,
                'url': url,
                'success': False,
                'error': str(e),
                'time': 0
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📈 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful_tests)}/{len(results)} tests")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)} tests")
    
    if successful_tests:
        avg_time = sum(r['time'] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average time: {avg_time:.2f} seconds")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['error']}")
    else:
        print(f"\n🎉 All tests passed! System is crash-proof.")
    
    print(f"\n🎯 Crash Prevention: {'SUCCESS' if len(failed_tests) == 0 else 'PARTIAL'}")

if __name__ == "__main__":
    test_robust_detector()