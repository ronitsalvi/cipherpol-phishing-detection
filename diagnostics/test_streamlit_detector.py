#!/usr/bin/env python3
"""
Test the detector as it's used in Streamlit
Check if there's a difference between direct usage and Streamlit usage
"""

import sys
import os
import time
import traceback
import json

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import exactly as Streamlit does
from modules.robust_phishing_detector import RobustPhishingDetector

class StreamlitDetectorTester:
    """Test detector exactly as Streamlit uses it"""
    
    def test_streamlit_style_usage(self):
        """Test detector usage that mimics Streamlit app"""
        
        print("🌐 STREAMLIT STYLE DETECTOR TESTING")
        print("=" * 50)
        print("Testing detector exactly as used in simple_app.py")
        
        results = {}
        
        # Test the cached detector loading (similar to Streamlit)
        print("\n📦 Testing Cached Detector Loading")
        print("-" * 30)
        
        try:
            # Simulate Streamlit's @st.cache_resource behavior
            print("Loading detector with caching simulation...")
            detector = self._load_detector_cached()
            print("✅ Cached detector loaded successfully")
            results['cached_loading'] = {'status': 'SUCCESS'}
        except Exception as e:
            print(f"❌ Cached detector loading failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['cached_loading'] = {'status': 'FAILED', 'error': str(e), 'traceback': traceback.format_exc()}
            return results
        
        # Test the exact URL that's failing in Streamlit
        problem_url = "https://github.com/new"
        
        print(f"\n🎯 Testing Problem URL: {problem_url}")
        print("-" * 30)
        
        try:
            print("Starting analysis (simulating Streamlit flow)...")
            start_time = time.time()
            
            # Simulate progress updates like Streamlit
            print("🔄 Analyzing URL...")
            
            result = detector.analyze_url(problem_url)
            analysis_time = time.time() - start_time
            
            print("✅ Analysis complete!")
            
            # Extract key results
            trust_score = result['trust_score']
            risk_level = result['risk_level']
            confidence = result['confidence']
            component_scores = result['component_scores']
            
            results['problem_url_test'] = {
                'status': 'SUCCESS',
                'url': problem_url,
                'trust_score': trust_score,
                'risk_level': risk_level,
                'confidence': confidence,
                'component_scores': component_scores,
                'analysis_time': analysis_time,
                'full_result': result
            }
            
            print(f"\n📊 RESULTS FOR {problem_url}:")
            print(f"   Trust Score: {trust_score}/100")
            print(f"   Risk Level: {risk_level}")
            print(f"   Confidence: {confidence}%")
            print(f"   Analysis Time: {analysis_time:.2f}s")
            print(f"   Component Scores:")
            print(f"     Domain: {component_scores.get('domain', 'N/A')}")
            print(f"     Content: {component_scores.get('content', 'N/A')}")
            print(f"     Technical: {component_scores.get('technical', 'N/A')}")
            
            # Check if this matches the Streamlit error
            if trust_score == 0 and risk_level == 'CRITICAL':
                print("🚨 PROBLEM REPRODUCED: Got CRITICAL RISK like Streamlit!")
                
                # Dig deeper into the explanations
                explanations = result.get('explanations', {})
                if explanations.get('error'):
                    print(f"   Error found: {explanations['error']}")
                    if explanations.get('details'):
                        print("   Error details:")
                        for detail in explanations['details']:
                            print(f"     • {detail}")
                else:
                    print("   No error in explanations - unexpected!")
            else:
                print("✅ DIFFERENT RESULT: Not reproducing Streamlit error")
        
        except Exception as e:
            print(f"💥 Analysis failed with exception: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['problem_url_test'] = {
                'status': 'EXCEPTION',
                'url': problem_url,
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        
        # Test multiple URLs to compare
        print(f"\n🧪 Testing Multiple URLs for Comparison")
        print("-" * 30)
        
        test_urls = [
            "https://github.com/new",
            "https://www.google.com",
            "https://www.instagram.com"
        ]
        
        results['comparison_test'] = {}
        
        for url in test_urls:
            print(f"\nTesting: {url}")
            try:
                start_time = time.time()
                result = detector.analyze_url(url)
                duration = time.time() - start_time
                
                trust_score = result['trust_score']
                risk_level = result['risk_level']
                
                results['comparison_test'][url] = {
                    'status': 'SUCCESS',
                    'trust_score': trust_score,
                    'risk_level': risk_level,
                    'duration': duration
                }
                
                status_emoji = "🔴" if risk_level == "CRITICAL" else ("🟡" if risk_level in ["HIGH", "MEDIUM"] else "🟢")
                print(f"  {status_emoji} {trust_score}/100 - {risk_level} ({duration:.2f}s)")
                
                # Flag any critical results
                if risk_level == "CRITICAL":
                    print(f"    🚨 CRITICAL DETECTED - This should not happen for legitimate URLs!")
                
            except Exception as e:
                results['comparison_test'][url] = {
                    'status': 'EXCEPTION',
                    'error': str(e)
                }
                print(f"  💥 Exception: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 STREAMLIT STYLE TEST SUMMARY")
        print("=" * 50)
        self._print_summary(results)
        
        return results
    
    def _load_detector_cached(self):
        """Simulate Streamlit's cached detector loading"""
        # This simulates what happens in simple_app.py with @st.cache_resource
        return RobustPhishingDetector()
    
    def _print_summary(self, results):
        """Print test summary"""
        
        # Check cached loading
        cached_result = results.get('cached_loading', {})
        if cached_result.get('status') == 'SUCCESS':
            print("✅ Cached Loading: SUCCESS")
        else:
            print("❌ Cached Loading: FAILED")
            return
        
        # Check problem URL test
        problem_test = results.get('problem_url_test', {})
        if problem_test.get('status') == 'SUCCESS':
            trust_score = problem_test.get('trust_score', 0)
            risk_level = problem_test.get('risk_level', 'UNKNOWN')
            
            if trust_score == 0 and risk_level == 'CRITICAL':
                print("🚨 Problem URL Test: REPRODUCED STREAMLIT ERROR")
                print("   Issue confirmed: GitHub URL getting CRITICAL RISK")
            else:
                print(f"🤔 Problem URL Test: DIFFERENT RESULT ({trust_score}/100 - {risk_level})")
                print("   This suggests the issue might be intermittent or context-specific")
        else:
            print("❌ Problem URL Test: FAILED")
        
        # Check comparison test
        comparison_test = results.get('comparison_test', {})
        critical_count = sum(1 for result in comparison_test.values() 
                           if result.get('risk_level') == 'CRITICAL')
        
        if critical_count > 0:
            print(f"🚨 Comparison Test: {critical_count}/{len(comparison_test)} URLs got CRITICAL")
            print("   Legitimate URLs are being flagged as critical - this is the core issue")
        else:
            print(f"✅ Comparison Test: All URLs got appropriate risk levels")
            print("   No critical risk flags for legitimate URLs")

def main():
    """Run Streamlit-style detector testing"""
    tester = StreamlitDetectorTester()
    results = tester.test_streamlit_style_usage()
    
    # Save results
    with open('/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1/diagnostics/streamlit_detector_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: streamlit_detector_test_results.json")

if __name__ == "__main__":
    main()