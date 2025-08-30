"""
Simple Phishing Detection Web App
Streamlined version for local deployment
"""

import streamlit as st
import time
from modules.robust_phishing_detector import RobustPhishingDetector

# Page configuration
st.set_page_config(
    page_title="Phishing Detection System",
    page_icon="🛡️",
    layout="wide"
)

def main():
    # Title and description
    st.title("🛡️ Explainable Phishing Detection System")
    st.markdown("**AI-powered fraud detection with transparent explanations**")
    
    # Initialize detector (cached for performance)
    @st.cache_resource
    def load_detector():
        return RobustPhishingDetector()
    
    # Add cache refresh button for debugging
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Cache", help="Clear cache and reload detector"):
            st.cache_resource.clear()
            st.rerun()
    
    try:
        detector = load_detector()
        st.success("✅ Detection system ready!")
        
        # Show cache status for debugging
        cache_info = f"Cache status: Detector loaded at {time.strftime('%H:%M:%S')}"
        st.info(cache_info)
        
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
                # Perform analysis
                start_time = time.time()
                result = detector.analyze_url(url_input)
                analysis_time = time.time() - start_time
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Display results
                display_results(result, analysis_time, detector)
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("This might be due to network issues or an unreachable URL.")
    
    # Sample URLs section
    st.header("🧪 Try Sample URLs")
    col1, col2, col3 = st.columns(3)
    
    sample_urls = [
        "https://www.google.com",
        "https://github.com",
        "https://httpbin.org"
    ]
    
    for i, sample_url in enumerate(sample_urls):
        with [col1, col2, col3][i]:
            if st.button(f"Test: {sample_url}", key=f"sample_{i}"):
                st.session_state.test_url = sample_url
                st.rerun()
    
    # System information
    with st.expander("ℹ️ System Information"):
        st.markdown("""
        ### Detection Methodology
        
        **Domain Analysis (35% weight):**
        - Domain age and registration patterns
        - TLD risk assessment
        - Suspicious character patterns
        
        **Content Analysis (40% weight):**
        - Suspicious keyword detection
        - Form security analysis
        - Content quality assessment
        
        **Technical Analysis (25% weight):**
        - SSL certificate validation
        - DNS configuration analysis
        - Security headers evaluation
        
        ### Risk Levels
        - 🟢 **LOW (70-100)**: Safe to use
        - 🟡 **MEDIUM (40-69)**: Use with caution
        - 🔴 **HIGH (20-39)**: Likely fraudulent
        - 🚨 **CRITICAL (0-19)**: Definite threat
        """)

def display_results(result, analysis_time, detector):
    """Display analysis results"""
    
    trust_score = result['trust_score']
    risk_level = result['risk_level']
    confidence = result['confidence']
    explanations = result['explanations']
    
    # Main results display
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Risk level with color coding
        if risk_level == 'LOW':
            st.success(f"🟢 Trust Score: {trust_score}/100 - LOW RISK")
        elif risk_level == 'MEDIUM':
            st.warning(f"🟡 Trust Score: {trust_score}/100 - MEDIUM RISK")
        elif risk_level == 'HIGH':
            st.error(f"🔴 Trust Score: {trust_score}/100 - HIGH RISK")
        else:
            st.error(f"🚨 Trust Score: {trust_score}/100 - CRITICAL RISK")
    
    with col2:
        st.metric("Confidence", f"{confidence}%")
    
    with col3:
        st.metric("Analysis Time", f"{analysis_time:.1f}s")
    
    # Component scores
    st.subheader("📊 Component Breakdown")
    component_scores = result['component_scores']
    
    # Show partial analysis warning if applicable
    analysis_status = result.get('analysis_status', {})
    if analysis_status.get('partial_analysis', False):
        successful = analysis_status.get('successful_modules', 0)
        total = analysis_status.get('total_modules', 3)
        st.warning(f"⚠️ Partial Analysis: {successful}/{total} modules completed successfully. Some features may be unavailable.")
    
    col1, col2, col3 = st.columns(3)
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
    
    # Detailed explanations
    st.subheader("📋 Detailed Analysis")
    
    # Handle error case
    if explanations.get('error'):
        st.error(f"❌ Analysis Error: {explanations['error']}")
        if explanations.get('details'):
            with st.expander("Error Details"):
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
    
    # Show neutral signals (errors/warnings)
    if explanations.get('neutral_signals'):
        with st.expander("ℹ️ Analysis Notes"):
            for signal in explanations['neutral_signals']:
                module = signal.get('module', 'Unknown')
                st.markdown(f"- **{signal['description']}** *[{module}]*")
                if signal.get('evidence'):
                    st.markdown(f"  *{signal['evidence']}*")
    
    # Recommendation
    st.subheader("💡 Recommendation")
    recommendation = detector.get_recommendation(result)
    
    if risk_level == 'LOW':
        st.success(recommendation)
    elif risk_level == 'MEDIUM':
        st.warning(recommendation)
    else:
        st.error(recommendation)

if __name__ == "__main__":
    main()