"""
Simple Phishing Detection Web App
Streamlined version for local deployment
"""

import os
# Fix OpenMP conflict before any imports
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import streamlit as st
import time
from modules.robust_phishing_detector import RobustPhishingDetector
from modules.visual_analyzer import create_visual_analyzer
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Phishing Detection System",
    page_icon="🛡️",
    layout="wide"
)

def main():
    # Title and description
    st.title("🛡️ Phishing Detection System")
    st.markdown("**AI-powered fraud detection with transparent explanations - Prepared for CipherCop 2025 Hackathon**")
    
    # Check if visual libraries are available
    def check_visual_availability():
        try:
            import torch
            import torchvision
            import faiss
            return True
        except ImportError:
            return False
    
    # Initialize detector (cached for performance with visual library detection)
    @st.cache_resource
    def load_detector(_visual_available=None):
        import os
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        try:
            return RobustPhishingDetector()
        except Exception as e:
            st.error(f"❌ Failed to initialize detector: {e}")
            raise
    
    # Initialize visual analyzer (cached for performance with dependency check)
    @st.cache_resource
    def load_visual_analyzer(_visual_available=None):
        import os
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        try:
            return create_visual_analyzer()
        except Exception as e:
            st.warning(f"⚠️ Visual analyzer failed to load: {e}")
            return None
    
    # Add cache refresh button for debugging
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Cache", help="Clear cache and reload detector"):
            st.cache_resource.clear()
            st.rerun()
    
    try:
        # Check visual library availability and pass to cache functions
        visual_available = check_visual_availability()
        
        detector = load_detector(_visual_available=visual_available)
        visual_analyzer = load_visual_analyzer(_visual_available=visual_available)
        
    except Exception as e:
        st.error(f"❌ System initialization failed: {e}")
        st.error("💡 Try clicking 'Refresh Cache' button to reload the detector")
        st.stop()
    
    # URL input section
    st.header("🔍 URL Analysis")
    
    # Handle test URL from session state
    default_url = ""
    if hasattr(st.session_state, 'test_url'):
        default_url = st.session_state.test_url
        delattr(st.session_state, 'test_url')
    
    url_input = st.text_input(
        "Enter URL to analyze:",
        value=default_url,
        placeholder="https://example.com",
        help="Enter the complete URL including http:// or https://"
    )
    
    # Visual analysis section
    uploaded_logo = None
    if visual_analyzer:
        with st.expander("🎨 Visual Brand Analysis (Optional)", expanded=False):
            st.markdown("Upload a logo image to verify brand authenticity against the website's domain.")
            
            uploaded_file = st.file_uploader(
                "Upload brand logo (optional):",
                type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
                help="Upload a logo image to check if it matches the website's claimed brand"
            )
            
            if uploaded_file is not None:
                try:
                    uploaded_logo = Image.open(uploaded_file).convert('RGB')
                    st.image(uploaded_logo, caption="Uploaded logo", width=150)
                    st.success("✅ Logo uploaded successfully")
                except Exception as e:
                    st.error(f"❌ Failed to process uploaded image: {e}")
            
    
    # Analysis button
    if st.button("🔍 Analyze URL", type="primary"):
        if not url_input:
            st.warning("Please enter a URL to analyze")
        elif not url_input.startswith(('http://', 'https://')):
            st.error("Please enter a valid URL starting with http:// or https://")
        else:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Analyzing URL...")
            progress_bar.progress(25)
            
            try:
                # Step 1: Perform traditional analysis first
                status_text.text("🔄 Running traditional analysis...")
                progress_bar.progress(50)
                
                start_time = time.time()
                
                # Use Gemini-enhanced analysis if available, otherwise visual analysis
                if hasattr(detector, 'analyze_url_with_gemini') and hasattr(detector, 'gemini_analyzer') and detector.gemini_analyzer:
                    result = detector.analyze_url_with_gemini(url_input, uploaded_logo)
                    visual_result = result.get('visual_analysis')
                elif visual_analyzer and hasattr(detector, 'analyze_url_with_visual'):
                    result = detector.analyze_url_with_visual(url_input, uploaded_logo)
                    visual_result = result.get('visual_analysis')
                else:
                    result = detector.analyze_url(url_input)
                    visual_result = None
                
                analysis_time = time.time() - start_time
                progress_bar.progress(100)
                
                # Check if Gemini analysis was included
                gemini_analysis = result.get('gemini_analysis', {})
                if gemini_analysis.get('status') == 'success':
                    status_text.text("✅ Complete analysis with AI validation!")
                else:
                    status_text.text("✅ Analysis complete!")
                
                # Display results
                display_results(result, visual_result, analysis_time, detector)
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("This might be due to network issues or an unreachable URL.")
    
    
    # System information
    with st.expander("ℹ️ System Information"):
        st.markdown("""
        ### Detection Methodology
        
        **Domain Analysis (30% weight):**
        - Domain age and registration patterns
        - TLD risk assessment
        - Suspicious character patterns
        - Typosquatting and homograph detection
        
        **Content Analysis (35% weight):**
        - Suspicious keyword detection
        - Form security analysis
        - Content quality assessment
        - Hidden element detection
        
        **Technical Analysis (20% weight):**
        - SSL certificate validation
        - DNS configuration analysis
        - Security headers evaluation
        
        **Visual Analysis (15% weight):**
        - Brand logo verification
        - Visual similarity matching
        - Logo database comparison
        
        **Company Database Whitelist:**
        - 32M+ verified company records
        - Automatic whitelisting for legitimate businesses
        - Fast-track analysis bypass (0.1s vs 5-10s)
        - Industry and company name verification
        
        ### Risk Levels
        - 🟢 **LOW (70-100)**: Safe to use
        - 🟡 **MEDIUM (40-69)**: Use with caution
        - 🔴 **HIGH (20-39)**: Likely fraudulent
        - 🚨 **CRITICAL (0-19)**: Definite threat
        """)

def display_results(result, visual_result, analysis_time, detector):
    """Display analysis results including visual analysis"""
    
    trust_score = result['trust_score']
    risk_level = result['risk_level']
    confidence = result['confidence']
    explanations = result['explanations']
    
    # Check if this is a whitelisted result
    analysis_status = result.get('analysis_status', {})
    is_whitelisted = analysis_status.get('whitelisted', False)
    
    # Special display for whitelisted domains
    if is_whitelisted:
        whitelist_info = result.get('whitelist_info', {})
        st.success(f"✅ VERIFIED LEGITIMATE COMPANY")
        st.markdown(f"**Company:** {whitelist_info.get('company_name', 'Unknown')}")
        st.markdown(f"**Industry:** {whitelist_info.get('industry', 'Unknown')}")
        st.markdown(f"**Website:** {whitelist_info.get('website', 'Unknown')}")
        st.info("🚀 **Fast Track Analysis**: This domain is in our verified company database. Comprehensive phishing analysis was bypassed.")
    
    # Display AI Expert Assessment (Primary)
    gemini_analysis = result.get('gemini_analysis', {})
    if gemini_analysis.get('status') == 'success':
        display_gemini_assessment(gemini_analysis, gemini_analysis.get('analysis_time', 0))
    
    # Always show Traditional Analysis in accordion (Secondary)
    with st.expander("📊 Traditional Analysis Details", expanded=False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric("Confidence", f"{confidence}%")
        
        with col2:
            st.metric("Analysis Time", f"{analysis_time:.1f}s")
        
        # Component scores
        st.markdown("**Component Breakdown:**")
        component_scores = result['component_scores']
        
        # Show partial analysis warning if applicable
        analysis_status = result.get('analysis_status', {})
        if analysis_status.get('partial_analysis', False):
            successful = analysis_status.get('successful_modules', 0)
            total = analysis_status.get('total_modules', 3)
            st.warning(f"⚠️ Partial Analysis: {successful}/{total} modules completed successfully. Some features may be unavailable.")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            domain_score = component_scores['domain']
            domain_display = f"{domain_score}/100" if domain_score != 'Error' else "Error"
            st.metric("Domain Analysis", domain_display)
        with col2:
            content_score = component_scores['content']
            content_display = f"{content_score}/100" if content_score != 'Error' else "Error"
            st.metric("Content Analysis", content_display)
        with col3:
            technical_score = component_scores['technical']
            technical_display = f"{technical_score}/100" if technical_score != 'Error' else "Error"
            st.metric("Technical Analysis", technical_display)
        with col4:
            visual_score = component_scores.get('visual', 'N/A')
            visual_display = f"{visual_score}/100" if visual_score not in ['Error', 'N/A'] else visual_score
            st.metric("Visual Analysis", visual_display)
        
        # Show detailed explanations inside accordion
        _display_traditional_explanations(explanations, visual_result)
    
    # Show traditional recommendation only if no AI available
    if gemini_analysis.get('status') != 'success':
        st.subheader("💡 Recommendation")
        recommendation = detector.get_recommendation(result)
        
        if risk_level == 'LOW':
            st.success(recommendation)
        elif risk_level == 'MEDIUM':
            st.warning(recommendation)
        else:
            st.error(recommendation)

def _display_traditional_explanations(explanations, visual_result):
    """Display traditional analysis explanations"""
    
    # Handle error case
    if explanations.get('error'):
        st.error(f"❌ Analysis Error: {explanations['error']}")
        if explanations.get('details'):
            st.markdown("**Error Details:**")
            for detail in explanations['details']:
                st.text(f"• {detail}")
        return
    
    # Risk factors
    if explanations.get('negative_signals'):
        st.markdown("#### ❌ Risk Factors Found:")
        for signal in explanations['negative_signals']:
            module = signal.get('module', 'Unknown')
            points = signal.get('points', 0)
            if points > 0:
                st.markdown(f"- **{signal['description']}** (-{points} points) *[{module}]*")
            else:
                st.markdown(f"- **{signal['description']}** *[{module}]*")
            if signal.get('evidence'):
                st.markdown(f"  *Evidence: {signal['evidence']}*")
    
    # Positive indicators
    if explanations.get('positive_signals'):
        st.markdown("#### ✅ Positive Indicators:")
        for signal in explanations['positive_signals']:
            module = signal.get('module', 'Unknown')
            points = signal.get('points', 0)
            if points > 0:
                st.markdown(f"- **{signal['description']}** (+{points} points) *[{module}]*")
            else:
                st.markdown(f"- **{signal['description']}** *[{module}]*")
    
    # Security considerations/warnings (new warning signals)
    warnings = explanations.get('warnings', [])
    if warnings:
        st.markdown("#### ⚠️ Security Considerations:")
        st.markdown("*The following are informational flags that do not affect the trust score but may require attention:*")
        
        for warning in warnings:
            category = warning.get('category', 'general')
            description = warning.get('description', 'Warning detected')
            evidence = warning.get('evidence', '')
            module = warning.get('module', 'Unknown')
            recommendation = warning.get('recommendation', '')
            
            # Display warning with appropriate icon
            if category == 'url_shortener':
                icon = "🔗"
            elif category == 'obfuscated_code':
                icon = "🔒"
            else:
                icon = "⚠️"
                
            st.markdown(f"{icon} **{description}** *[{module}]*")
            if evidence:
                st.markdown(f"   *Evidence: {evidence}*")
            if recommendation:
                st.markdown(f"   *Note: {recommendation}*")
    
    # Visual analysis results
    if visual_result:
        display_visual_analysis(visual_result)
    
    # Show neutral signals (errors/warnings)
    if explanations.get('neutral_signals'):
        st.markdown("#### ℹ️ Analysis Notes:")
        for signal in explanations['neutral_signals']:
            module = signal.get('module', 'Unknown')
            st.markdown(f"- **{signal['description']}** *[{module}]*")
            if signal.get('evidence'):
                st.markdown(f"  *{signal['evidence']}*")

def display_visual_analysis(visual_result):
    """Display visual analysis results"""
    
    st.markdown("#### 🎨 Visual Brand Analysis")
    
    # Handle visual analysis errors/warnings
    visual_warnings = visual_result.get('warnings', [])
    if visual_warnings:
        for warning in visual_warnings:
            if warning.get('category') == 'visual_analysis':
                st.warning(f"⚠️ {warning['description']}: {warning['evidence']}")
                if warning.get('recommendation'):
                    st.info(f"💡 {warning['recommendation']}")
        return
    
    # Brand verification status
    brand_verification = visual_result.get('brand_verification', {})
    status = brand_verification.get('status', 'no_analysis')
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if status == 'match':
            st.success(f"✅ Brand Verified: {brand_verification.get('reason', 'Brand matches domain')}")
        elif status == 'mismatch':
            st.error(f"❌ Brand Mismatch: {brand_verification.get('reason', 'Brand does not match domain')}")
        elif status == 'uncertain':
            st.warning(f"⚠️ Uncertain: {brand_verification.get('reason', 'Brand verification unclear')}")
        elif status == 'no_logos':
            st.info("ℹ️ No logos detected on page for verification")
        elif status == 'disabled':
            st.info("ℹ️ Visual analysis disabled - install required libraries")
        else:
            st.info("ℹ️ No visual analysis performed")
    
    with col2:
        if brand_verification.get('similarity'):
            similarity = brand_verification['similarity']
            confidence = brand_verification.get('confidence', 'Unknown')
            st.metric("Logo Similarity", f"{similarity:.3f}", f"{confidence} Confidence")
    
    # Logo matching results
    logo_matches = visual_result.get('logo_matches', [])
    if logo_matches:
        st.markdown("#### 🔍 Logo Matching Details:")
        st.markdown("**Top logo matches found:**")
        
        for match in logo_matches[:2]:  # Show top 2 matches
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.markdown(f"**{match['brand'].title()}**")
            with col2:
                st.metric("Similarity", f"{match['similarity']:.3f}")
            with col3:
                st.markdown(f"*{match['confidence']}*")
            with col4:
                domains = match.get('domains', [])
                if domains:
                    st.markdown(f"*Expected: {', '.join(domains[:2])}*")
    
    # Visual analysis explanations (if any)
    visual_explanations = visual_result.get('explanations', [])
    if visual_explanations:
        st.markdown("**Visual Analysis Details:**")
        for explanation in visual_explanations:
            exp_type = explanation.get('type', 'neutral')
            if exp_type == 'negative':
                st.markdown(f"❌ {explanation['description']} (-{explanation.get('points', 0)} points)")
            elif exp_type == 'positive':
                st.markdown(f"✅ {explanation['description']} (+{explanation.get('points', 0)} points)")
            else:
                st.markdown(f"ℹ️ {explanation['description']}")
            
            if explanation.get('evidence'):
                st.markdown(f"   *Evidence: {explanation['evidence']}*")

def display_gemini_assessment(gemini_result, analysis_time):
    """Display Gemini LLM assessment results"""
    
    st.markdown("## 🤖 AI Expert Assessment")
    
    if gemini_result['status'] != 'success':
        st.warning("⚠️ AI validation unavailable - using traditional analysis only")
        return
    
    assessment = gemini_result.get('gemini_assessment', {})
    verdict = assessment.get('verdict', 'unavailable')
    confidence = assessment.get('confidence', 0)
    reasoning = assessment.get('reasoning', 'No reasoning provided')
    recommendation = assessment.get('recommendation', 'Use traditional analysis above')
    
    # Display verdict with appropriate styling
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if verdict == 'safe':
            st.success(f"✅ **AI Assessment**: SAFE WEBSITE")
        elif verdict == 'suspicious':
            st.warning(f"⚠️ **AI Assessment**: SUSPICIOUS WEBSITE")
        elif verdict == 'malicious':
            st.error(f"❌ **AI Assessment**: MALICIOUS WEBSITE")
        else:
            st.info(f"ℹ️ **AI Assessment**: ANALYSIS UNAVAILABLE")
    
    with col2:
        st.metric("AI Confidence", f"{confidence}%")
    
    with col3:
        st.metric("AI Response Time", f"{analysis_time:.1f}s")
    
    # Show AI reasoning
    st.markdown("#### 🧠 AI Expert Reasoning:")
    st.markdown(f"*{reasoning}*")
    
    # Show AI recommendation
    st.markdown("#### 💡 AI Recommendation:")
    if verdict == 'safe':
        st.success(f"✅ {recommendation}")
    elif verdict == 'suspicious':
        st.warning(f"⚠️ {recommendation}")
    elif verdict == 'malicious':
        st.error(f"❌ {recommendation}")
    else:
        st.info(f"ℹ️ {recommendation}")
    
    # Show critical factors if available
    critical_factors = assessment.get('critical_factors', [])
    if critical_factors:
        st.markdown("#### ⚡ Key Factors Considered:")
        for factor in critical_factors:
            st.markdown(f"• {factor}")

if __name__ == "__main__":
    main()