#!/usr/bin/env python3
"""
Test Individual Analyzer Modules
Debug which specific analyzer is failing and why
"""

import sys
import os
import time
import traceback

# Add the parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.domain_analyzer import DomainAnalyzer
from modules.content_analyzer import ContentAnalyzer
from modules.technical_analyzer import TechnicalAnalyzer

class AnalyzerTester:
    """Test individual analyzer modules"""
    
    def __init__(self):
        self.test_urls = [
            'https://github.com/new',
            'https://www.google.com',
            'https://www.instagram.com',
            'https://httpbin.org/html'
        ]
    
    def test_all_analyzers(self):
        """Test all analyzer modules"""
        
        print("🧪 ANALYZER MODULE TESTING")
        print("=" * 50)
        
        results = {
            'domain_analyzer': {},
            'content_analyzer': {},
            'technical_analyzer': {}
        }
        
        # Test Domain Analyzer
        print("\n🌐 Testing Domain Analyzer")
        print("-" * 30)
        results['domain_analyzer'] = self._test_domain_analyzer()
        
        # Test Content Analyzer
        print("\n📝 Testing Content Analyzer") 
        print("-" * 30)
        results['content_analyzer'] = self._test_content_analyzer()
        
        # Test Technical Analyzer
        print("\n🔧 Testing Technical Analyzer")
        print("-" * 30)
        results['technical_analyzer'] = self._test_technical_analyzer()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TESTING SUMMARY")
        print("=" * 50)
        self._print_summary(results)
        
        return results
    
    def _test_domain_analyzer(self):
        """Test domain analyzer module"""
        
        results = {}
        
        try:
            analyzer = DomainAnalyzer()
            print("✅ Domain analyzer initialized successfully")
            
            for url in self.test_urls:
                print(f"\nTesting: {url}")
                try:
                    start_time = time.time()
                    result = analyzer.analyze_domain(url)
                    duration = time.time() - start_time
                    
                    if 'error' in result:
                        results[url] = {
                            'status': 'ERROR',
                            'error': result['error'],
                            'duration': duration
                        }
                        print(f"  ❌ Error: {result['error']} ({duration:.3f}s)")
                    else:
                        score = result.get('score', 0)
                        explanations = len(result.get('explanations', []))
                        results[url] = {
                            'status': 'SUCCESS',
                            'score': score,
                            'explanations_count': explanations,
                            'duration': duration
                        }
                        print(f"  ✅ Success: Score={score}, Explanations={explanations} ({duration:.3f}s)")
                
                except Exception as e:
                    results[url] = {
                        'status': 'EXCEPTION',
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                    print(f"  💥 Exception: {e}")
                    print(f"     Traceback: {traceback.format_exc()}")
        
        except Exception as e:
            print(f"❌ Domain analyzer initialization failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['initialization_error'] = str(e)
        
        return results
    
    def _test_content_analyzer(self):
        """Test content analyzer module"""
        
        results = {}
        
        try:
            analyzer = ContentAnalyzer()
            print("✅ Content analyzer initialized successfully")
            
            for url in self.test_urls:
                print(f"\nTesting: {url}")
                try:
                    start_time = time.time()
                    result = analyzer.analyze_content(url)
                    duration = time.time() - start_time
                    
                    if 'error' in result:
                        results[url] = {
                            'status': 'ERROR',
                            'error': result['error'],
                            'duration': duration
                        }
                        print(f"  ❌ Error: {result['error']} ({duration:.3f}s)")
                    else:
                        score = result.get('score', 0)
                        explanations = len(result.get('explanations', []))
                        results[url] = {
                            'status': 'SUCCESS',
                            'score': score,
                            'explanations_count': explanations,
                            'duration': duration
                        }
                        print(f"  ✅ Success: Score={score}, Explanations={explanations} ({duration:.3f}s)")
                
                except Exception as e:
                    results[url] = {
                        'status': 'EXCEPTION',
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                    print(f"  💥 Exception: {e}")
                    print(f"     Traceback: {traceback.format_exc()}")
        
        except Exception as e:
            print(f"❌ Content analyzer initialization failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['initialization_error'] = str(e)
        
        return results
    
    def _test_technical_analyzer(self):
        """Test technical analyzer module"""
        
        results = {}
        
        try:
            analyzer = TechnicalAnalyzer()
            print("✅ Technical analyzer initialized successfully")
            
            for url in self.test_urls:
                print(f"\nTesting: {url}")
                try:
                    start_time = time.time()
                    result = analyzer.analyze_technical(url)
                    duration = time.time() - start_time
                    
                    if 'error' in result:
                        results[url] = {
                            'status': 'ERROR',
                            'error': result['error'],
                            'duration': duration
                        }
                        print(f"  ❌ Error: {result['error']} ({duration:.3f}s)")
                    else:
                        score = result.get('score', 0)
                        explanations = len(result.get('explanations', []))
                        results[url] = {
                            'status': 'SUCCESS',
                            'score': score,
                            'explanations_count': explanations,
                            'duration': duration
                        }
                        print(f"  ✅ Success: Score={score}, Explanations={explanations} ({duration:.3f}s)")
                
                except Exception as e:
                    results[url] = {
                        'status': 'EXCEPTION',
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                    print(f"  💥 Exception: {e}")
                    print(f"     Traceback: {traceback.format_exc()}")
        
        except Exception as e:
            print(f"❌ Technical analyzer initialization failed: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            results['initialization_error'] = str(e)
        
        return results
    
    def _print_summary(self, results):
        """Print testing summary"""
        
        for analyzer_name, analyzer_results in results.items():
            print(f"\n{analyzer_name.upper()}:")
            
            if 'initialization_error' in analyzer_results:
                print(f"  ❌ Initialization failed: {analyzer_results['initialization_error']}")
                continue
            
            success_count = 0
            error_count = 0
            exception_count = 0
            
            for url, result in analyzer_results.items():
                if result['status'] == 'SUCCESS':
                    success_count += 1
                elif result['status'] == 'ERROR':
                    error_count += 1
                elif result['status'] == 'EXCEPTION':
                    exception_count += 1
            
            total_tests = len(self.test_urls)
            print(f"  ✅ Success: {success_count}/{total_tests}")
            print(f"  ❌ Errors: {error_count}/{total_tests}")
            print(f"  💥 Exceptions: {exception_count}/{total_tests}")
            
            if success_count == 0:
                print(f"  🚨 CRITICAL: All tests failed for {analyzer_name}")
            elif success_count < total_tests:
                print(f"  ⚠️  PARTIAL: Some tests failed for {analyzer_name}")
            else:
                print(f"  🎉 EXCELLENT: All tests passed for {analyzer_name}")

def main():
    """Run analyzer testing"""
    tester = AnalyzerTester()
    results = tester.test_all_analyzers()
    
    # Save results
    import json
    with open('/Users/ronitsalvi/Documents/Ronit Personal/Projects/Hackathon 1/diagnostics/analyzer_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: analyzer_test_results.json")

if __name__ == "__main__":
    main()