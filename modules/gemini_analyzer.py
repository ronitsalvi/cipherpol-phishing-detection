"""
Gemini LLM Analyzer for Final Security Assessment
Provides AI-powered validation of phishing detection results
"""

import json
import logging
import requests
from typing import Dict, Optional, Any
import time

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """
    AI-powered final validation using Google's Gemini LLM
    Analyzes complete detection results to provide expert-level assessment
    """
    
    def __init__(self, api_key: str = "AIzaSyDlwtCyXrlhQzMCAvK8QEEbh46D2AFf-xc"):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.timeout = 120  # 2 minute timeout for Gemini 2.5 Flash
        
    def analyze_with_llm(self, url: str, analysis_result: Dict) -> Dict:
        """
        Send complete analysis to Gemini for expert assessment
        
        Args:
            url: The analyzed URL
            analysis_result: Complete result from traditional analysis
            
        Returns:
            Dict with Gemini's assessment and reasoning
        """
        
        try:
            # Prepare structured data for Gemini
            structured_data = self._prepare_analysis_data(url, analysis_result)
            
            # Create prompt for Gemini
            prompt = self._create_gemini_prompt(structured_data)
            
            # Send to Gemini API
            logger.info(f"🧠 Sending analysis to Gemini for expert assessment...")
            start_time = time.time()
            
            # Log request payload for testing
            self._log_request_payload(url, structured_data, prompt)
            
            response = self._send_to_gemini(prompt)
            
            analysis_time = time.time() - start_time
            logger.info(f"✅ Gemini analysis completed in {analysis_time:.2f}s")
            
            # Log response payload for testing
            self._log_response_payload(url, response)
            
            # Parse and validate response
            parsed_result = self._parse_gemini_response(response)
            
            return {
                'status': 'success',
                'analysis_time': analysis_time,
                'gemini_assessment': parsed_result
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Gemini analysis failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'gemini_assessment': {
                    'verdict': 'unavailable',
                    'confidence': 0,
                    'reasoning': 'LLM analysis unavailable - using traditional assessment only'
                }
            }
    
    def _prepare_analysis_data(self, url: str, result: Dict) -> Dict:
        """Prepare structured data for Gemini analysis"""
        
        # Extract key components
        trust_score = result.get('trust_score', 0)
        risk_level = result.get('risk_level', 'UNKNOWN')
        confidence = result.get('confidence', 0)
        component_scores = result.get('component_scores', {})
        explanations = result.get('explanations', {})
        
        # Organize negative signals (risk factors)
        risk_factors = []
        for signal in explanations.get('negative_signals', []):
            risk_factors.append({
                'factor': signal.get('description', ''),
                'points_deducted': signal.get('points', 0),
                'evidence': signal.get('evidence', ''),
                'module': signal.get('module', '')
            })
        
        # Organize positive signals (trust indicators)
        trust_indicators = []
        for signal in explanations.get('positive_signals', []):
            trust_indicators.append({
                'indicator': signal.get('description', ''),
                'points_added': signal.get('points', 0),
                'evidence': signal.get('evidence', ''),
                'module': signal.get('module', '')
            })
        
        # Visual analysis results
        visual_analysis = result.get('visual_analysis', {})
        brand_verification = visual_analysis.get('brand_verification', {})
        
        # Company database status
        analysis_status = result.get('analysis_status', {})
        is_whitelisted = analysis_status.get('whitelisted', False)
        whitelist_info = result.get('whitelist_info', {})
        
        return {
            'url': url,
            'traditional_assessment': {
                'trust_score': trust_score,
                'risk_level': risk_level,
                'confidence': confidence,
                'component_scores': component_scores
            },
            'risk_factors': risk_factors,
            'trust_indicators': trust_indicators,
            'brand_verification': {
                'status': brand_verification.get('status', 'no_analysis'),
                'reasoning': brand_verification.get('reason', ''),
                'similarity': brand_verification.get('similarity', 0)
            },
            'company_whitelist': {
                'is_whitelisted': is_whitelisted,
                'company_name': whitelist_info.get('company_name', ''),
                'industry': whitelist_info.get('industry', '')
            },
            'analysis_metadata': {
                'successful_modules': analysis_status.get('successful_modules', 0),
                'total_modules': analysis_status.get('total_modules', 4),
                'partial_analysis': analysis_status.get('partial_analysis', False)
            }
        }
    
    def _create_gemini_prompt(self, data: Dict) -> str:
        """Create structured prompt for Gemini analysis"""
        
        return f"""You are a cybersecurity expert analyzing a website for phishing threats. Please provide your expert assessment based on the comprehensive analysis data below.

WEBSITE ANALYSIS DATA:
======================

URL: {data['url']}

TRADITIONAL SYSTEM ASSESSMENT:
- Trust Score: {data['traditional_assessment']['trust_score']}/100
- Risk Level: {data['traditional_assessment']['risk_level']}
- Analysis Confidence: {data['traditional_assessment']['confidence']}%

COMPONENT SCORES:
- Domain Analysis: {data['traditional_assessment']['component_scores'].get('domain', 'N/A')}
- Content Analysis: {data['traditional_assessment']['component_scores'].get('content', 'N/A')}
- Technical Analysis: {data['traditional_assessment']['component_scores'].get('technical', 'N/A')}
- Visual Analysis: {data['traditional_assessment']['component_scores'].get('visual', 'N/A')}

IDENTIFIED RISK FACTORS:
{json.dumps(data['risk_factors'], indent=2)}

TRUST INDICATORS:
{json.dumps(data['trust_indicators'], indent=2)}

BRAND VERIFICATION:
- Status: {data['brand_verification']['status']}
- Reasoning: {data['brand_verification']['reasoning']}
- Logo Similarity: {data['brand_verification']['similarity']}

COMPANY DATABASE:
- Whitelisted: {data['company_whitelist']['is_whitelisted']}
- Company: {data['company_whitelist']['company_name']}
- Industry: {data['company_whitelist']['industry']}

ANALYSIS STATUS:
- Modules Successful: {data['analysis_metadata']['successful_modules']}/{data['analysis_metadata']['total_modules']}
- Partial Analysis: {data['analysis_metadata']['partial_analysis']}

EXPERT ASSESSMENT REQUEST:
==========================

Based on your cybersecurity expertise and the comprehensive analysis above, provide your assessment in the following JSON format:

{{
    "verdict": "safe" | "suspicious" | "malicious",
    "confidence": <number 0-100>,
    "reasoning": "<2-3 sentence explanation of your assessment>",
    "critical_factors": ["<list of most important factors that influenced your decision>"],
    "recommendation": "<specific action recommendation for the user>"
}}

Consider the following in your assessment:
1. Company whitelist status (if whitelisted, likely legitimate)
2. Brand verification results (mismatches indicate impersonation)
3. Pattern of risk factors vs trust indicators
4. Severity and credibility of identified threats
5. Overall coherence of the security profile

Focus on sophisticated phishing detection that rule-based systems might miss. Your assessment should complement the traditional analysis.

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT."""

    def _send_to_gemini(self, prompt: str) -> Dict:
        """Send prompt to Gemini API and get response"""
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _parse_gemini_response(self, response: Dict) -> Dict:
        """Parse and validate Gemini's JSON response"""
        
        try:
            # Extract text from Gemini response structure
            candidates = response.get('candidates', [])
            if not candidates:
                raise Exception("No response candidates from Gemini")
            
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise Exception("No content parts in Gemini response")
            
            response_text = parts[0].get('text', '')
            
            # Parse JSON from response text
            # Remove any potential markdown formatting
            json_text = response_text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            parsed = json.loads(json_text)
            
            # Validate required fields
            required_fields = ['verdict', 'confidence', 'reasoning', 'recommendation']
            for field in required_fields:
                if field not in parsed:
                    raise Exception(f"Missing required field: {field}")
            
            # Validate verdict values
            valid_verdicts = ['safe', 'suspicious', 'malicious']
            if parsed['verdict'] not in valid_verdicts:
                raise Exception(f"Invalid verdict: {parsed['verdict']}")
            
            # Validate confidence range
            confidence = parsed['confidence']
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
                raise Exception(f"Invalid confidence value: {confidence}")
            
            return parsed
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini JSON response: {e}")
        except Exception as e:
            raise Exception(f"Failed to validate Gemini response: {e}")
    
    def _log_request_payload(self, url: str, structured_data: Dict, prompt: str):
        """Log request payload for testing and debugging"""
        
        import os
        
        # Create safe filename from URL
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
        safe_filename = f"gemini_request_{safe_url}_{int(time.time())}.json"
        
        request_data = {
            'timestamp': time.time(),
            'url': url,
            'structured_data': structured_data,
            'prompt': prompt,
            'api_endpoint': self.base_url,
            'timeout': self.timeout
        }
        
        try:
            os.makedirs("Gemini Test Delete", exist_ok=True)
            with open(f"Gemini Test Delete/{safe_filename}", 'w') as f:
                json.dump(request_data, f, indent=2)
            logger.info(f"📝 Request payload logged to: Gemini Test Delete/{safe_filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to log request payload: {e}")
    
    def _log_response_payload(self, url: str, response: Dict):
        """Log response payload for testing and debugging"""
        
        import os
        
        # Create safe filename from URL
        safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
        safe_filename = f"gemini_response_{safe_url}_{int(time.time())}.json"
        
        response_data = {
            'timestamp': time.time(),
            'url': url,
            'raw_response': response,
            'api_endpoint': self.base_url
        }
        
        try:
            os.makedirs("Gemini Test Delete", exist_ok=True)
            with open(f"Gemini Test Delete/{safe_filename}", 'w') as f:
                json.dump(response_data, f, indent=2)
            logger.info(f"📝 Response payload logged to: Gemini Test Delete/{safe_filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to log response payload: {e}")

def create_gemini_analyzer(api_key: str = "AIzaSyDlwtCyXrlhQzMCAvK8QEEbh46D2AFf-xc") -> Optional[GeminiAnalyzer]:
    """
    Factory function to create Gemini analyzer with error handling
    
    Returns:
        GeminiAnalyzer instance or None if initialization fails
    """
    
    try:
        analyzer = GeminiAnalyzer(api_key)
        logger.info("✅ Gemini analyzer initialized successfully")
        return analyzer
        
    except Exception as e:
        logger.warning(f"⚠️ Gemini analyzer initialization failed: {e}")
        return None