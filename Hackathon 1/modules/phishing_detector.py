"""
Phishing Detector Module
Main orchestrator that combines all analysis modules for explainable fraud detection
"""

from .domain_analyzer import DomainAnalyzer
from .content_analyzer import ContentAnalyzer  
from .technical_analyzer import TechnicalAnalyzer
from typing import Dict, List
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PhishingDetector:
    """Main phishing detection system with explainable AI"""
    
    def __init__(self):
        # Initialize all analyzer modules
        self.domain_analyzer = DomainAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # Scoring weights for different components
        self.weights = {
            'domain': 0.35,      # 35% weight - domain characteristics
            'content': 0.40,     # 40% weight - content analysis
            'technical': 0.25    # 25% weight - technical infrastructure
        }
        
        # Base trust score (neutral starting point)
        self.base_score = 70
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 5,      # 5+ signals for high confidence
            'medium': 3,    # 3-4 signals for medium confidence
            'low': 1        # 1-2 signals for low confidence
        }
    
    def analyze_url(self, url: str) -> Dict:
        """Perform comprehensive analysis of a URL with explanations"""
        
        start_time = time.time()
        
        try:
            logger.info(f"Starting analysis of: {url}")
            
            # Parallel analysis from all modules
            domain_result = self.domain_analyzer.analyze_domain(url)
            content_result = self.content_analyzer.analyze_content(url)
            technical_result = self.technical_analyzer.analyze_technical(url)
            
            # Check for critical errors
            errors = []
            if 'error' in domain_result:
                errors.append(f"Domain analysis: {domain_result['error']}")
            if 'error' in content_result:
                errors.append(f"Content analysis: {content_result['error']}")
            if 'error' in technical_result:
                errors.append(f"Technical analysis: {technical_result['error']}")
            
            # If we have too many errors, return error result
            if len(errors) >= 2:
                return {
                    'url': url,
                    'trust_score': 0,
                    'risk_level': 'ERROR',
                    'confidence': 0,
                    'explanations': {'error': 'Multiple analysis modules failed', 'details': errors},
                    'analysis_time': time.time() - start_time
                }
            
            # Combine results
            combined_result = self._combine_analysis_results(
                url, domain_result, content_result, technical_result
            )
            
            combined_result['analysis_time'] = time.time() - start_time
            logger.info(f"Analysis completed in {combined_result['analysis_time']:.2f} seconds")
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Analysis failed for {url}: {e}")
            return {
                'url': url,
                'trust_score': 0,
                'risk_level': 'ERROR',
                'confidence': 0,
                'explanations': {'error': f'Analysis failed: {str(e)}'},
                'analysis_time': time.time() - start_time
            }
    
    def _combine_analysis_results(self, url: str, domain_result: Dict, 
                                content_result: Dict, technical_result: Dict) -> Dict:
        """Combine results from all analysis modules"""
        
        # Extract scores (handle errors gracefully)
        domain_score = domain_result.get('score', 0) if 'error' not in domain_result else 0
        content_score = content_result.get('score', 0) if 'error' not in content_result else 0
        technical_score = technical_result.get('score', 0) if 'error' not in technical_result else 0
        
        # Calculate weighted final score
        weighted_score = (
            domain_score * self.weights['domain'] +
            content_score * self.weights['content'] + 
            technical_score * self.weights['technical']
        )
        
        # Convert to 0-100 trust score (base score + weighted adjustments)
        trust_score = max(0, min(100, self.base_score + weighted_score))
        
        # Combine explanations
        all_explanations = self._combine_explanations(
            domain_result, content_result, technical_result
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(all_explanations)
        
        # Determine risk level
        risk_level = self._determine_risk_level(trust_score)
        
        return {
            'url': url,
            'trust_score': int(trust_score),
            'risk_level': risk_level,
            'confidence': confidence,
            'explanations': all_explanations,
            'component_scores': {
                'domain': int(self.base_score + domain_score) if domain_score != 0 else 'Error',
                'content': int(self.base_score + content_score) if content_score != 0 else 'Error', 
                'technical': int(self.base_score + technical_score) if technical_score != 0 else 'Error'
            },
            'weights_used': self.weights.copy()
        }
    
    def _combine_explanations(self, domain_result: Dict, content_result: Dict, 
                            technical_result: Dict) -> Dict:
        """Combine explanations from all modules"""
        
        negative_signals = []
        positive_signals = []
        neutral_signals = []
        
        # Process domain explanations
        if 'explanations' in domain_result:
            for exp in domain_result['explanations']:
                exp['module'] = 'Domain Analysis'
                if exp['type'] == 'negative':
                    negative_signals.append(exp)
                elif exp['type'] == 'positive':
                    positive_signals.append(exp)
                else:
                    neutral_signals.append(exp)
        
        # Process content explanations
        if 'explanations' in content_result:
            for exp in content_result['explanations']:
                exp['module'] = 'Content Analysis'
                if exp['type'] == 'negative':
                    negative_signals.append(exp)
                elif exp['type'] == 'positive':
                    positive_signals.append(exp)
                else:
                    neutral_signals.append(exp)
        
        # Process technical explanations
        if 'explanations' in technical_result:
            for exp in technical_result['explanations']:
                exp['module'] = 'Technical Analysis'
                if exp['type'] == 'negative':
                    negative_signals.append(exp)
                elif exp['type'] == 'positive':
                    positive_signals.append(exp)
                else:
                    neutral_signals.append(exp)
        
        # Sort by points (highest impact first)
        negative_signals.sort(key=lambda x: x.get('points', 0), reverse=True)
        positive_signals.sort(key=lambda x: x.get('points', 0), reverse=True)
        
        return {
            'negative_signals': negative_signals,
            'positive_signals': positive_signals,
            'neutral_signals': neutral_signals,
            'summary': self._generate_explanation_summary(negative_signals, positive_signals)
        }
    
    def _generate_explanation_summary(self, negative_signals: List[Dict], 
                                    positive_signals: List[Dict]) -> Dict:
        """Generate a summary of the key findings"""
        
        total_negative_points = sum(signal.get('points', 0) for signal in negative_signals)
        total_positive_points = sum(signal.get('points', 0) for signal in positive_signals)
        
        # Identify the most significant issues
        top_concerns = negative_signals[:3]  # Top 3 concerns
        top_positives = positive_signals[:3]  # Top 3 positive indicators
        
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
    
    def _calculate_confidence(self, explanations: Dict) -> int:
        """Calculate confidence level based on number and strength of signals"""
        
        negative_signals = explanations['negative_signals']
        positive_signals = explanations['positive_signals']
        
        # Count strong signals (high point values)
        strong_negative = len([s for s in negative_signals if s.get('points', 0) >= 10])
        strong_positive = len([s for s in positive_signals if s.get('points', 0) >= 8])
        
        total_strong_signals = strong_negative + strong_positive
        total_signals = len(negative_signals) + len(positive_signals)
        
        # Calculate confidence percentage
        if total_strong_signals >= self.confidence_thresholds['high']:
            confidence = 85 + min(15, total_strong_signals * 3)  # 85-100%
        elif total_signals >= self.confidence_thresholds['medium']:
            confidence = 65 + min(20, total_signals * 5)  # 65-85%
        elif total_signals >= self.confidence_thresholds['low']:
            confidence = 40 + min(25, total_signals * 10)  # 40-65%
        else:
            confidence = 25  # Low confidence with few signals
        
        return min(100, confidence)
    
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
        
        trust_score = result['trust_score']
        risk_level = result['risk_level']
        confidence = result['confidence']
        
        if risk_level == 'LOW':
            if confidence >= 80:
                return "✅ This website appears legitimate and safe to use. Standard internet precautions apply."
            else:
                return "✅ This website appears mostly safe, but we have limited data. Proceed with normal caution."
                
        elif risk_level == 'MEDIUM':
            if confidence >= 70:
                return "⚠️ This website shows some suspicious characteristics. Verify its legitimacy before entering personal information."
            else:
                return "⚠️ We detected some concerning signs but lack complete information. Exercise additional caution."
                
        elif risk_level == 'HIGH':
            return "🔴 This website shows strong indicators of being fraudulent. Avoid entering personal or financial information."
            
        else:  # CRITICAL
            return "🚨 DANGER: This website shows critical signs of being a phishing or scam site. Do not use this website or enter any information."
    
    def batch_analyze(self, urls: List[str]) -> List[Dict]:
        """Analyze multiple URLs in batch"""
        
        results = []
        total_urls = len(urls)
        
        logger.info(f"Starting batch analysis of {total_urls} URLs")
        
        for i, url in enumerate(urls, 1):
            try:
                logger.info(f"Processing URL {i}/{total_urls}: {url}")
                result = self.analyze_url(url)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to analyze {url}: {e}")
                results.append({
                    'url': url,
                    'trust_score': 0,
                    'risk_level': 'ERROR',
                    'confidence': 0,
                    'explanations': {'error': str(e)},
                    'analysis_time': 0
                })
        
        logger.info(f"Batch analysis completed: {total_urls} URLs processed")
        return results

if __name__ == "__main__":
    # Test the phishing detector
    detector = PhishingDetector()
    
    test_urls = [
        "https://www.google.com",
        "https://httpbin.org/html"
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Analyzing: {url}")
        print(f"{'='*60}")
        
        result = detector.analyze_url(url)
        
        print(f"Trust Score: {result['trust_score']}/100")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Analysis Time: {result['analysis_time']:.2f}s")
        
        print(f"\nRecommendation: {detector.get_recommendation(result)}")
        
        print(f"\nComponent Scores:")
        for component, score in result['component_scores'].items():
            print(f"  {component.title()}: {score}")
        
        explanations = result['explanations']
        
        if explanations.get('negative_signals'):
            print(f"\n❌ Risk Factors ({len(explanations['negative_signals'])}):")
            for signal in explanations['negative_signals'][:5]:  # Show top 5
                print(f"  • {signal['description']} (-{signal.get('points', 0)} pts) [{signal['module']}]")
        
        if explanations.get('positive_signals'):
            print(f"\n✅ Positive Indicators ({len(explanations['positive_signals'])}):")
            for signal in explanations['positive_signals'][:3]:  # Show top 3
                print(f"  • {signal['description']} (+{signal.get('points', 0)} pts) [{signal['module']}]")