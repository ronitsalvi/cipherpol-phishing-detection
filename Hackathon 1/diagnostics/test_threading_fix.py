#!/usr/bin/env python3
"""
Test the threading fix for RobustPhishingDetector
Verify that GitHub URL now gets correct LOW RISK score
"""

import sys
import os
import time
import threading

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.robust_phishing_detector import RobustPhishingDetector

def test_in_background_thread():
    """Test analyzer in background thread (simulates Streamlit environment)"""
    
    print("🧵 THREADING FIX TEST")
    print("=" * 40)
    print("Testing RobustPhishingDetector in background thread")
    print("(This simulates Streamlit's threading environment)")
    
    test_url = "https://github.com/new"
    results = {}
    
    def run_analysis():
        """Run analysis in background thread"""
        try:
            print(f"\n🔄 Thread {threading.current_thread().name}: Starting analysis...")
            detector = RobustPhishingDetector()
            
            start_time = time.time()
            result = detector.analyze_url(test_url)
            duration = time.time() - start_time
            
            trust_score = result['trust_score']
            risk_level = result['risk_level']
            confidence = result['confidence']
            component_scores = result['component_scores']
            
            results['success'] = True
            results['trust_score'] = trust_score
            results['risk_level'] = risk_level
            results['confidence'] = confidence
            results['component_scores'] = component_scores
            results['duration'] = duration
            results['full_result'] = result
            
            print(f"✅ Analysis completed in background thread!")
            print(f"   Trust Score: {trust_score}/100")
            print(f"   Risk Level: {risk_level}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Components: D:{component_scores.get('domain', 'N/A')} C:{component_scores.get('content', 'N/A')} T:{component_scores.get('technical', 'N/A')}")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            print(f"❌ Analysis failed in background thread: {e}")
    
    # Run in background thread
    thread = threading.Thread(target=run_analysis, name="AnalysisThread")
    thread.start()
    thread.join(timeout=120)  # 2 minute timeout for the thread itself
    
    if thread.is_alive():
        print("⏰ Thread timed out after 2 minutes")
        results['success'] = False
        results['error'] = "Thread timeout"
    
    # Print results
    print("\n" + "=" * 40)
    print("📊 THREADING TEST RESULTS")
    print("=" * 40)
    
    if results.get('success'):
        trust_score = results['trust_score']
        risk_level = results['risk_level']
        
        if trust_score == 0 and risk_level == 'CRITICAL':
            print("🚨 THREADING ISSUE STILL EXISTS")
            print("   GitHub URL still getting CRITICAL RISK")
            print("   Signal threading conflict not resolved")
        elif risk_level == 'LOW' and trust_score >= 70:
            print("🎉 THREADING FIX SUCCESSFUL!")
            print(f"   GitHub URL now gets {trust_score}/100 - {risk_level}")
            print("   Threading conflict resolved!")
        else:
            print(f"🤔 UNEXPECTED RESULT: {trust_score}/100 - {risk_level}")
            print("   Threading works but score is unexpected")
    else:
        error = results.get('error', 'Unknown error')
        print(f"❌ THREADING TEST FAILED: {error}")
        if 'signal only works in main thread' in error:
            print("   Signal threading conflict still exists")
        else:
            print("   Different error - may be network or other issue")
    
    return results

def main():
    """Run threading fix test"""
    print(f"🎯 Testing URL: https://github.com/new")
    print("Expected: LOW RISK (~84/100) instead of CRITICAL (0/100)")
    print()
    
    results = test_in_background_thread()
    
    # Save results
    import json
    with open('/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1/diagnostics/threading_fix_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: threading_fix_test_results.json")

if __name__ == "__main__":
    main()