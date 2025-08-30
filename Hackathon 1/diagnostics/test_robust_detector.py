#!/usr/bin/env python3
"""
Test RobustPhishingDetector to identify where it's failing
Since individual analyzers work, the issue must be in the detector itself
"""

import sys
import os
import time
import traceback
import json

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.robust_phishing_detector import RobustPhishingDetector

class RobustDetectorTester:
    """Test the RobustPhishingDetector to find where it fails"""
    
    def __init__(self):
        self.test_urls = [
            'https://github.com/new',
            'https://www.google.com',
            'https://www.instagram.com',
            'https://httpbin.org/html'
        ]
    
    def test_robust_detector(self):
        """Test the robust detector step by step"""
        
        print("🛡️ ROBUST DETECTOR TESTING")
        print("=" * 50)
        
        results = {}
        
        # Test initialization
        print("\n🏗️ Testing Initialization")
        print("-" * 30)
        try:
            start_time = time.time()
            detector = RobustPhishingDetector()
            init_time = time.time() - start_time
            print(f"✅ Detector initialized successfully ({init_time:.3f}s)")
            results['initialization'] = {'status': 'SUCCESS', 'duration': init_time}
        except Exception as e:
            print(f"❌ Detector initialization failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['initialization'] = {'status': 'FAILED', 'error': str(e), 'traceback': traceback.format_exc()}
            return results
        
        # Test URL validation
        print("\n🔍 Testing URL Validation")
        print("-" * 30)
        results['url_validation'] = {}
        
        for url in self.test_urls:
            try:
                is_valid, validated_url = detector._validate_url(url)
                results['url_validation'][url] = {
                    'is_valid': is_valid,
                    'validated_url': validated_url,
                    'status': 'SUCCESS' if is_valid else 'INVALID'
                }
                status_emoji = "✅" if is_valid else "❌"
                print(f"  {status_emoji} {url}: {'Valid' if is_valid else 'Invalid'}")
            except Exception as e:
                results['url_validation'][url] = {
                    'status': 'EXCEPTION',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                print(f"  💥 {url}: Exception - {e}")
        
        # Test individual analyzer calls through safe_analyzer_call
        print("\n🔧 Testing Safe Analyzer Calls")
        print("-" * 30)
        
        test_url = 'https://github.com/new'  # Focus on GitHub URL that's failing
        print(f"Testing with: {test_url}")
        
        results['safe_analyzer_calls'] = {}
        
        # Test domain analyzer call
        print("\n  🌐 Testing Domain Analyzer Call")
        try:
            start_time = time.time()
            domain_result = detector._safe_analyzer_call(
                'Domain',
                detector.domain_analyzer.analyze_domain,
                test_url
            )
            duration = time.time() - start_time
            
            results['safe_analyzer_calls']['domain'] = {
                'status': 'SUCCESS' if 'error' not in domain_result else 'ERROR',
                'result': domain_result,
                'duration': duration
            }
            
            if 'error' in domain_result:
                print(f"    ❌ Domain call failed: {domain_result['error']} ({duration:.3f}s)")
            else:
                score = domain_result.get('score', 0)
                print(f"    ✅ Domain call succeeded: Score={score} ({duration:.3f}s)")
        except Exception as e:
            results['safe_analyzer_calls']['domain'] = {
                'status': 'EXCEPTION',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"    💥 Domain call exception: {e}")
        
        # Test content analyzer call
        print("  📝 Testing Content Analyzer Call")
        try:
            start_time = time.time()
            content_result = detector._safe_analyzer_call(
                'Content',
                detector.content_analyzer.analyze_content,
                test_url
            )
            duration = time.time() - start_time
            
            results['safe_analyzer_calls']['content'] = {
                'status': 'SUCCESS' if 'error' not in content_result else 'ERROR',
                'result': content_result,
                'duration': duration
            }
            
            if 'error' in content_result:
                print(f"    ❌ Content call failed: {content_result['error']} ({duration:.3f}s)")
            else:
                score = content_result.get('score', 0)
                print(f"    ✅ Content call succeeded: Score={score} ({duration:.3f}s)")
        except Exception as e:
            results['safe_analyzer_calls']['content'] = {
                'status': 'EXCEPTION',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"    💥 Content call exception: {e}")
        
        # Test technical analyzer call
        print("  🔧 Testing Technical Analyzer Call")
        try:
            start_time = time.time()
            technical_result = detector._safe_analyzer_call(
                'Technical',
                detector.technical_analyzer.analyze_technical,
                test_url
            )
            duration = time.time() - start_time
            
            results['safe_analyzer_calls']['technical'] = {
                'status': 'SUCCESS' if 'error' not in technical_result else 'ERROR',
                'result': technical_result,
                'duration': duration
            }
            
            if 'error' in technical_result:
                print(f"    ❌ Technical call failed: {technical_result['error']} ({duration:.3f}s)")
            else:
                score = technical_result.get('score', 0)
                print(f"    ✅ Technical call succeeded: Score={score} ({duration:.3f}s)")
        except Exception as e:
            results['safe_analyzer_calls']['technical'] = {
                'status': 'EXCEPTION',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            print(f"    💥 Technical call exception: {e}")
        
        # Test full analysis
        print(f"\n🎯 Testing Full Analysis")
        print("-" * 30)
        results['full_analysis'] = {}
        
        for url in self.test_urls:
            print(f"\nTesting full analysis: {url}")
            try:
                start_time = time.time()
                result = detector.analyze_url(url)
                duration = time.time() - start_time
                
                trust_score = result.get('trust_score', 0)
                risk_level = result.get('risk_level', 'UNKNOWN')
                confidence = result.get('confidence', 0)
                
                results['full_analysis'][url] = {
                    'status': 'SUCCESS',
                    'trust_score': trust_score,
                    'risk_level': risk_level,
                    'confidence': confidence,
                    'duration': duration,
                    'full_result': result
                }
                
                print(f"  ✅ Success: {trust_score}/100 - {risk_level} (confidence: {confidence}%) ({duration:.3f}s)")
                
                # Check component scores
                component_scores = result.get('component_scores', {})
                print(f"      Components: D:{component_scores.get('domain', 'N/A')} C:{component_scores.get('content', 'N/A')} T:{component_scores.get('technical', 'N/A')}")
                
                # Check analysis status
                analysis_status = result.get('analysis_status', {})
                if analysis_status.get('partial_analysis'):
                    successful = analysis_status.get('successful_modules', 0)
                    total = analysis_status.get('total_modules', 3)
                    print(f"      Status: Partial analysis ({successful}/{total} modules successful)")
                else:
                    print(f"      Status: Full analysis completed")
                
            except Exception as e:
                results['full_analysis'][url] = {
                    'status': 'EXCEPTION',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                print(f"  💥 Exception: {e}")
                print(f"     Traceback: {traceback.format_exc()}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TESTING SUMMARY")
        print("=" * 50)
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results):
        """Print testing summary"""
        
        # Initialization summary
        init_result = results.get('initialization', {})
        if init_result.get('status') == 'SUCCESS':
            print("✅ Initialization: SUCCESS")
        else:
            print("❌ Initialization: FAILED")
            return
        
        # URL validation summary
        validation_results = results.get('url_validation', {})
        valid_count = sum(1 for r in validation_results.values() if r.get('is_valid', False))
        print(f"🔍 URL Validation: {valid_count}/{len(validation_results)} URLs valid")
        
        # Safe analyzer calls summary
        analyzer_calls = results.get('safe_analyzer_calls', {})
        success_count = sum(1 for r in analyzer_calls.values() if r.get('status') == 'SUCCESS')
        print(f"🔧 Safe Analyzer Calls: {success_count}/{len(analyzer_calls)} successful")
        
        if success_count < len(analyzer_calls):
            print("   🚨 Some analyzer calls are failing!")
            for name, result in analyzer_calls.items():
                if result.get('status') != 'SUCCESS':
                    print(f"      ❌ {name}: {result.get('error', 'Unknown error')}")
        
        # Full analysis summary
        full_analysis = results.get('full_analysis', {})
        analysis_success = sum(1 for r in full_analysis.values() if r.get('status') == 'SUCCESS')
        critical_risk_count = sum(1 for r in full_analysis.values() 
                                 if r.get('risk_level') == 'CRITICAL')
        
        print(f"🎯 Full Analysis: {analysis_success}/{len(full_analysis)} successful")
        
        if critical_risk_count > 0:
            print(f"   🚨 WARNING: {critical_risk_count} URLs getting CRITICAL RISK")
            for url, result in full_analysis.items():
                if result.get('risk_level') == 'CRITICAL':
                    trust_score = result.get('trust_score', 0)
                    print(f"      🔴 {url}: {trust_score}/100 - CRITICAL")

def main():
    """Run robust detector testing"""
    tester = RobustDetectorTester()
    results = tester.test_robust_detector()
    
    # Save results
    with open('/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1/diagnostics/robust_detector_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: robust_detector_test_results.json")

if __name__ == "__main__":
    main()