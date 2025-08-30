"""
Robust Phishing Detector Module  
Crash-proof version with comprehensive error handling and timeouts
"""

from .domain_analyzer import DomainAnalyzer
from .content_analyzer import ContentAnalyzer  
from .technical_analyzer import TechnicalAnalyzer
from typing import Dict, List, Tuple
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import sys
import gc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def execute_with_timeout(func, timeout_seconds, *args, **kwargs):
    """Execute function with thread-safe timeout"""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except FutureTimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")

class TimeoutError(Exception):
    """Custom timeout exception for compatibility"""
    pass

class RobustPhishingDetector:
    """Crash-proof phishing detection system with robust error handling"""
    
    def __init__(self):
        # Initialize all analyzer modules
        try:
            self.domain_analyzer = DomainAnalyzer()
            self.content_analyzer = ContentAnalyzer()
            self.technical_analyzer = TechnicalAnalyzer()
            logger.info("✅ All analyzers initialized successfully")
        except Exception as e:
            logger.error(f"❌ Analyzer initialization failed: {e}")
            raise
        
        # Scoring weights for different components
        self.weights = {
            'domain': 0.35,      # 35% weight - domain characteristics
            'content': 0.40,     # 40% weight - content analysis
            'technical': 0.25    # 25% weight - technical infrastructure
        }
        
        # Base trust score (neutral starting point)
        self.base_score = 70
        
        # Timeout settings (in seconds)
        self.timeouts = {
            'domain': 15,        # Domain analysis timeout
            'content': 30,       # Content analysis timeout (longer for complex pages)
            'technical': 20,     # Technical analysis timeout
            'total': 60          # Total analysis timeout
        }
        
        # Resource limits
        self.limits = {
            'max_content_size': 5 * 1024 * 1024,  # 5MB max content
            'max_redirects': 5,                    # Max redirect follow
            'request_timeout': 15                  # HTTP request timeout
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 5,      # 5+ signals for high confidence
            'medium': 3,    # 3-4 signals for medium confidence
            'low': 1        # 1-2 signals for low confidence
        }
    
    def _safe_analyzer_call(self, analyzer_name: str, analyzer_func, *args, **kwargs) -> Dict:
        """Safely call an analyzer with timeout and error handling"""
        
        result = {'error': f'{analyzer_name} analysis failed', 'score': 0, 'explanations': []}
        
        try:
            logger.info(f"🔄 Starting {analyzer_name} analysis...")
            
            # Use thread-safe timeout
            timeout_seconds = self.timeouts.get(analyzer_name.lower(), 30)
            
            # Execute analyzer with thread-safe timeout
            result = execute_with_timeout(
                analyzer_func, 
                timeout_seconds, 
                *args, 
                **kwargs
            )
            
            # Validate result
            if not isinstance(result, dict):
                raise ValueError(f"Invalid result format from {analyzer_name}")
            
            logger.info(f"✅ {analyzer_name} analysis completed successfully")
            return result
                
        except TimeoutError:
            logger.warning(f"⏰ {analyzer_name} analysis timed out after {timeout_seconds}s")
            return {
                'error': f'{analyzer_name} analysis timed out',
                'score': 0,
                'explanations': [{
                    'type': 'neutral',
                    'description': f'{analyzer_name} analysis timed out',
                    'evidence': f'Analysis exceeded {timeout_seconds} second limit'
                }]
            }
            
        except MemoryError:
            logger.warning(f"💾 {analyzer_name} analysis ran out of memory")
            gc.collect()  # Force garbage collection
            return {
                'error': f'{analyzer_name} analysis - memory limit exceeded',
                'score': 0,
                'explanations': [{
                    'type': 'neutral',
                    'description': f'{analyzer_name} analysis - resource limit exceeded',
                    'evidence': 'Content too large or complex for analysis'
                }]
            }
            
        except Exception as e:
            logger.warning(f"⚠️ {analyzer_name} analysis failed: {str(e)[:100]}")
            return {
                'error': f'{analyzer_name} analysis failed: {str(e)[:50]}',
                'score': 0,
                'explanations': [{
                    'type': 'neutral',
                    'description': f'{analyzer_name} analysis encountered an error',
                    'evidence': f'Error: {str(e)[:50]}'
                }]
            }
    
    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate and sanitize input URL"""
        
        if not url or not isinstance(url, str):
            return False, "Invalid URL format"
        
        url = url.strip()
        
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        if len(url) > 2048:  # Reasonable URL length limit
            return False, "URL is too long (max 2048 characters)"
        
        # Check for suspicious patterns that might cause crashes
        suspicious_patterns = [
            'javascript:',
            'data:',
            'file:',
            'ftp:',
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return False, f"Unsupported URL scheme: {pattern}"
        
        return True, url
    
    def analyze_url(self, url: str) -> Dict:
        """Perform comprehensive analysis of a URL with robust error handling"""
        
        overall_start_time = time.time()
        
        try:
            logger.info(f"🛡️ Starting robust analysis of: {url}")
            
            # Validate URL first
            is_valid, validated_url = self._validate_url(url)
            if not is_valid:
                return {
                    'url': url,
                    'trust_score': 0,
                    'risk_level': 'ERROR',
                    'confidence': 0,
                    'explanations': {
                        'error': f'URL validation failed: {validated_url}',
                        'negative_signals': [],
                        'positive_signals': [],
                        'neutral_signals': []
                    },
                    'component_scores': {'domain': 'Error', 'content': 'Error', 'technical': 'Error'},
                    'analysis_time': time.time() - overall_start_time
                }
            
            # Use the validated URL
            url = validated_url
            
            # Initialize results with error handling
            analysis_results = {}
            successful_analyses = 0
            
            # Domain Analysis (most reliable, fastest)
            logger.info("🌐 Starting domain analysis...")
            domain_result = self._safe_analyzer_call(
                'Domain', 
                self.domain_analyzer.analyze_domain, 
                url
            )
            analysis_results['domain'] = domain_result
            if 'error' not in domain_result:
                successful_analyses += 1
            
            # Technical Analysis (medium reliability)
            logger.info("🔧 Starting technical analysis...")
            technical_result = self._safe_analyzer_call(
                'Technical',
                self.technical_analyzer.analyze_technical,
                url
            )
            analysis_results['technical'] = technical_result
            if 'error' not in technical_result:
                successful_analyses += 1
            
            # Content Analysis (most likely to fail/timeout)  
            logger.info("📝 Starting content analysis...")
            content_result = self._safe_analyzer_call(
                'Content',
                self.content_analyzer.analyze_content,
                url
            )
            analysis_results['content'] = content_result
            if 'error' not in content_result:
                successful_analyses += 1
            
            logger.info(f"📊 Completed analyses: {successful_analyses}/3 successful")
            
            # If no analyses succeeded, return error
            if successful_analyses == 0:
                return {
                    'url': url,
                    'trust_score': 0,
                    'risk_level': 'ERROR',
                    'confidence': 0,
                    'explanations': {
                        'error': 'All analysis modules failed - URL may be unreachable or problematic',
                        'details': [
                            domain_result.get('error', 'Domain analysis failed'),
                            content_result.get('error', 'Content analysis failed'),
                            technical_result.get('error', 'Technical analysis failed')
                        ]
                    },
                    'component_scores': {'domain': 'Error', 'content': 'Error', 'technical': 'Error'},
                    'analysis_time': time.time() - overall_start_time
                }
            
            # Combine results with partial failure handling
            combined_result = self._combine_analysis_results_robust(
                url, domain_result, content_result, technical_result
            )
            
            combined_result['analysis_time'] = time.time() - overall_start_time
            combined_result['successful_analyses'] = f"{successful_analyses}/3"
            
            logger.info(f"✅ Analysis completed successfully in {combined_result['analysis_time']:.2f} seconds")
            
            return combined_result
            
        except Exception as e:
            logger.error(f"💥 Critical error in analysis for {url}: {e}")
            return {
                'url': url,
                'trust_score': 0,
                'risk_level': 'ERROR', 
                'confidence': 0,
                'explanations': {
                    'error': f'Critical analysis error: {str(e)[:100]}',
                    'negative_signals': [],
                    'positive_signals': [],
                    'neutral_signals': []
                },
                'component_scores': {'domain': 'Error', 'content': 'Error', 'technical': 'Error'},
                'analysis_time': time.time() - overall_start_time
            }
    
    def _combine_analysis_results_robust(self, url: str, domain_result: Dict, 
                                       content_result: Dict, technical_result: Dict) -> Dict:
        """Combine results with robust partial failure handling"""
        
        # Extract scores (handle errors gracefully)
        domain_score = domain_result.get('score', 0) if 'error' not in domain_result else 0
        content_score = content_result.get('score', 0) if 'error' not in content_result else 0
        technical_score = technical_result.get('score', 0) if 'error' not in technical_result else 0
        
        # Count successful analyses for weight adjustment
        successful_analyses = sum([
            'error' not in domain_result,
            'error' not in content_result, 
            'error' not in technical_result
        ])
        
        # Adjust weights based on successful analyses
        if successful_analyses > 0:
            if 'error' not in domain_result and 'error' not in technical_result and 'error' in content_result:
                # If only content failed, redistribute its weight
                adjusted_weights = {'domain': 0.6, 'content': 0, 'technical': 0.4}
            elif 'error' not in domain_result and 'error' in technical_result and 'error' in content_result:
                # If only domain succeeded
                adjusted_weights = {'domain': 1.0, 'content': 0, 'technical': 0}  
            elif 'error' in domain_result and 'error' not in content_result and 'error' not in technical_result:
                # If only domain failed
                adjusted_weights = {'domain': 0, 'content': 0.6, 'technical': 0.4}
            else:
                # Use original weights for successful analyses
                adjusted_weights = self.weights.copy()
        else:
            adjusted_weights = {'domain': 0, 'content': 0, 'technical': 0}
        
        # Calculate weighted final score
        weighted_score = (
            domain_score * adjusted_weights['domain'] +
            content_score * adjusted_weights['content'] + 
            technical_score * adjusted_weights['technical']
        )
        
        # Convert to 0-100 trust score 
        trust_score = max(0, min(100, self.base_score + weighted_score))
        
        # Combine explanations with error handling
        all_explanations = self._combine_explanations_robust(
            domain_result, content_result, technical_result
        )
        
        # Calculate confidence based on successful analyses
        confidence = self._calculate_confidence_robust(all_explanations, successful_analyses)
        
        # Determine risk level
        risk_level = self._determine_risk_level(trust_score)
        
        # Create component scores
        component_scores = {
            'domain': int(self.base_score + domain_score) if 'error' not in domain_result else 'Error',
            'content': int(self.base_score + content_score) if 'error' not in content_result else 'Error', 
            'technical': int(self.base_score + technical_score) if 'error' not in technical_result else 'Error'
        }
        
        return {
            'url': url,
            'trust_score': int(trust_score),
            'risk_level': risk_level,
            'confidence': confidence,
            'explanations': all_explanations,
            'component_scores': component_scores,
            'weights_used': adjusted_weights,
            'analysis_status': {
                'successful_modules': successful_analyses,
                'total_modules': 3,
                'partial_analysis': successful_analyses < 3
            }
        }
    
    def _combine_explanations_robust(self, domain_result: Dict, content_result: Dict, 
                                   technical_result: Dict) -> Dict:
        """Combine explanations with error handling"""
        
        negative_signals = []
        positive_signals = []
        neutral_signals = []
        warnings = []  # New: collect warning signals
        
        # Process each result safely
        results = [
            ('Domain Analysis', domain_result),
            ('Content Analysis', content_result),
            ('Technical Analysis', technical_result)
        ]
        
        for module_name, result in results:
            if 'error' in result:
                # Add error as neutral signal
                neutral_signals.append({
                    'type': 'neutral',
                    'description': f'{module_name} unavailable',
                    'evidence': result['error'],
                    'module': module_name
                })
            else:
                # Process explanations if available
                explanations = result.get('explanations', [])
                for exp in explanations:
                    exp['module'] = module_name
                    if exp.get('type') == 'negative':
                        negative_signals.append(exp)
                    elif exp.get('type') == 'positive':
                        positive_signals.append(exp)
                    else:
                        neutral_signals.append(exp)
                
                # Process warning signals if available (from content analyzer)
                result_warnings = result.get('warnings', [])
                for warning in result_warnings:
                    warning['module'] = module_name
                    warnings.append(warning)
        
        # Sort by points (highest impact first)
        negative_signals.sort(key=lambda x: x.get('points', 0), reverse=True)
        positive_signals.sort(key=lambda x: x.get('points', 0), reverse=True)
        
        return {
            'negative_signals': negative_signals,
            'positive_signals': positive_signals,
            'neutral_signals': neutral_signals,
            'warnings': warnings,  # New: include warning signals
            'summary': self._generate_explanation_summary_robust(negative_signals, positive_signals)
        }
    
    def _generate_explanation_summary_robust(self, negative_signals: List[Dict], 
                                           positive_signals: List[Dict]) -> Dict:
        """Generate explanation summary with robust handling"""
        
        total_negative_points = sum(signal.get('points', 0) for signal in negative_signals)
        total_positive_points = sum(signal.get('points', 0) for signal in positive_signals)
        
        # Identify the most significant issues (safely)
        top_concerns = negative_signals[:3] if negative_signals else []
        top_positives = positive_signals[:3] if positive_signals else []
        
        # Generate category breakdown
        category_issues = {
            'Domain Analysis': len([s for s in negative_signals if s.get('module') == 'Domain Analysis']),
            'Content Analysis': len([s for s in negative_signals if s.get('module') == 'Content Analysis']),
            'Technical Analysis': len([s for s in negative_signals if s.get('module') == 'Technical Analysis'])
        }
        
        most_problematic_category = max(category_issues, key=category_issues.get) if any(category_issues.values()) else None
        
        return {
            'total_negative_points': total_negative_points,
            'total_positive_points': total_positive_points,
            'top_concerns': top_concerns,
            'top_positives': top_positives,
            'most_problematic_category': most_problematic_category,
            'category_breakdown': category_issues
        }
    
    def _calculate_confidence_robust(self, explanations: Dict, successful_analyses: int) -> int:
        """Calculate confidence with robust handling"""
        
        # Base confidence on successful analyses
        base_confidence = (successful_analyses / 3) * 60  # 0-60 based on successful modules
        
        negative_signals = explanations.get('negative_signals', [])
        positive_signals = explanations.get('positive_signals', [])
        
        # Count strong signals
        strong_negative = len([s for s in negative_signals if s.get('points', 0) >= 10])
        strong_positive = len([s for s in positive_signals if s.get('points', 0) >= 8])
        
        total_strong_signals = strong_negative + strong_positive
        
        # Add confidence based on signal strength
        signal_confidence = min(30, total_strong_signals * 8)
        
        # Add confidence based on signal count
        total_signals = len(negative_signals) + len(positive_signals)
        count_confidence = min(10, total_signals * 2)
        
        final_confidence = int(base_confidence + signal_confidence + count_confidence)
        
        return min(100, final_confidence)
    
    def _determine_risk_level(self, trust_score: int) -> str:
        """Determine risk level based on trust score"""
        
        if trust_score >= 70:
            return 'LOW'
        elif trust_score >= 40:
            return 'MEDIUM'
        elif trust_score >= 20:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def get_recommendation(self, result: Dict) -> str:
        """Generate user-friendly recommendation based on analysis"""
        
        trust_score = result.get('trust_score', 0)
        risk_level = result.get('risk_level', 'ERROR')
        confidence = result.get('confidence', 0)
        analysis_status = result.get('analysis_status', {})
        
        # Handle partial analysis
        if analysis_status.get('partial_analysis', False):
            partial_note = f" (Based on {analysis_status['successful_modules']}/{analysis_status['total_modules']} analysis modules)"
        else:
            partial_note = ""
        
        if risk_level == 'ERROR':
            return "⚠️ Unable to analyze this URL. It may be unreachable, blocked, or contain unsupported content."
        elif risk_level == 'LOW':
            if confidence >= 80:
                return f"✅ This website appears legitimate and safe to use{partial_note}. Standard internet precautions apply."
            else:
                return f"✅ This website appears mostly safe{partial_note}, but analysis was limited. Proceed with normal caution."
        elif risk_level == 'MEDIUM':
            return f"⚠️ This website shows some suspicious characteristics{partial_note}. Verify its legitimacy before entering personal information."
        elif risk_level == 'HIGH':
            return f"🔴 This website shows strong indicators of being fraudulent{partial_note}. Avoid entering personal or financial information."
        else:  # CRITICAL
            return f"🚨 DANGER: This website shows critical signs of being a phishing or scam site{partial_note}. Do not use this website or enter any information."