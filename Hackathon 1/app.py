"""
Explainable Phishing Detection System
A transparent, rule-based system for detecting phishing websites with detailed explanations.
"""

import streamlit as st
import pandas as pd
from modules.phishing_detector import PhishingDetector
from modules.data_loader import DataLoader
import time

def main():
    st.set_page_config(
        page_title="Phishing Detection System",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🛡️ Explainable Phishing Detection System")
    st.markdown("**Transparent AI-powered fraud detection with detailed explanations**")
    
    # Sidebar
    st.sidebar.header("System Information")
    st.sidebar.markdown("**Accuracy Target:** 75-80%")
    st.sidebar.markdown("**Analysis Time:** ~15-30 seconds")
    st.sidebar.markdown("**Detection Focus:** Phishing & Scam Websites")
    
    # Initialize detector
    @st.cache_resource
    def load_detector():
        return PhishingDetector()
    
    detector = load_detector()
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["🔍 URL Analysis", "📊 Batch Analysis", "ℹ️ System Info"])
    
    with tab1:
        st.header("Single URL Analysis")
        
        # URL input
        url_input = st.text_input(
            "Enter URL to analyze:",
            placeholder="https://example.com",
            help="Enter the full URL including http:// or https://"
        )
        
        analyze_button = st.button("🔍 Analyze URL", type="primary")
        
        if analyze_button and url_input:
            if not url_input.startswith(('http://', 'https://')):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("Analyzing URL... This may take 15-30 seconds"):
                    start_time = time.time()
                    
                    try:
                        result = detector.analyze_url(url_input)
                        analysis_time = time.time() - start_time
                        
                        # Display results
                        display_analysis_results(result, analysis_time)
                        
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
                        st.info("This might be due to network issues or an unreachable URL.")
    
    with tab2:
        st.header("Batch URL Analysis")
        st.markdown("Upload a CSV file with URLs or enter multiple URLs")
        
        # File upload
        uploaded_file = st.file_uploader("Upload CSV file", type="csv", help="CSV should have a 'url' column")
        
        # Text area for multiple URLs
        st.markdown("**Or enter multiple URLs (one per line):**")
        urls_text = st.text_area("URLs:", height=150, placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com")
        
        batch_analyze_button = st.button("🔍 Analyze Batch", type="primary")
        
        if batch_analyze_button:
            urls_to_analyze = []
            
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                if 'url' in df.columns:
                    urls_to_analyze = df['url'].tolist()
                else:
                    st.error("CSV file must contain a 'url' column")
            
            if urls_text.strip():
                urls_from_text = [url.strip() for url in urls_text.split('\n') if url.strip()]
                urls_to_analyze.extend(urls_from_text)
            
            if urls_to_analyze:
                perform_batch_analysis(detector, urls_to_analyze)
            else:
                st.warning("Please provide URLs either via file upload or text input")
    
    with tab3:
        st.header("System Information")
        display_system_info()

def display_analysis_results(result, analysis_time):
    """Display detailed analysis results with explanations"""
    
    trust_score = result['trust_score']
    explanations = result['explanations']
    confidence = result['confidence']
    
    # Trust Score Display
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Color coding based on trust score
        if trust_score >= 70:
            score_color = "🟢"
            risk_level = "LOW RISK"
            color = "success"
        elif trust_score >= 40:
            score_color = "🟡"
            risk_level = "MEDIUM RISK"
            color = "warning"
        else:
            score_color = "🔴"
            risk_level = "HIGH RISK"
            color = "error"
        
        st.markdown(f"## {score_color} TRUST SCORE: {trust_score}/100")
        st.markdown(f"**Risk Level:** {risk_level}")
    
    with col2:
        st.metric("Confidence", f"{confidence}%")
    
    with col3:
        st.metric("Analysis Time", f"{analysis_time:.1f}s")
    
    # Detailed Explanations
    st.header("📋 Analysis Breakdown")
    
    if explanations['negative_signals']:
        st.subheader("❌ Risk Factors Found:")
        for signal in explanations['negative_signals']:
            st.markdown(f"- **{signal['description']}** (-{signal['points']} points)")
            if signal.get('evidence'):
                st.markdown(f"  *Evidence: {signal['evidence']}*")
    
    if explanations['positive_signals']:
        st.subheader("✅ Positive Indicators:")
        for signal in explanations['positive_signals']:
            st.markdown(f"- **{signal['description']}** (+{signal['points']} points)")
    
    if explanations['neutral_signals']:
        st.subheader("ℹ️ Neutral Factors:")
        for signal in explanations['neutral_signals']:
            st.markdown(f"- {signal['description']}")
    
    # Recommendation
    st.header("🎯 Recommendation")
    if trust_score >= 70:
        st.success("This website appears to be legitimate. Proceed with normal caution.")
    elif trust_score >= 40:
        st.warning("This website shows some suspicious indicators. Exercise additional caution and verify authenticity.")
    else:
        st.error("This website shows strong indicators of being fraudulent or malicious. Avoid entering personal information or conducting transactions.")

def perform_batch_analysis(detector, urls):
    """Perform batch analysis on multiple URLs"""
    progress_bar = st.progress(0)
    results = []
    
    for i, url in enumerate(urls):
        try:
            result = detector.analyze_url(url)
            results.append({
                'URL': url,
                'Trust Score': result['trust_score'],
                'Risk Level': 'HIGH' if result['trust_score'] < 40 else 'MEDIUM' if result['trust_score'] < 70 else 'LOW',
                'Confidence': f"{result['confidence']}%"
            })
        except Exception as e:
            results.append({
                'URL': url,
                'Trust Score': 'Error',
                'Risk Level': 'Error',
                'Confidence': str(e)[:50]
            })
        
        progress_bar.progress((i + 1) / len(urls))
    
    # Display results
    st.subheader("📊 Batch Analysis Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    valid_results = [r for r in results if r['Trust Score'] != 'Error']
    
    with col1:
        high_risk = len([r for r in valid_results if isinstance(r['Trust Score'], (int, float)) and r['Trust Score'] < 40])
        st.metric("High Risk URLs", high_risk)
    
    with col2:
        medium_risk = len([r for r in valid_results if isinstance(r['Trust Score'], (int, float)) and 40 <= r['Trust Score'] < 70])
        st.metric("Medium Risk URLs", medium_risk)
    
    with col3:
        low_risk = len([r for r in valid_results if isinstance(r['Trust Score'], (int, float)) and r['Trust Score'] >= 70])
        st.metric("Low Risk URLs", low_risk)

def display_system_info():
    """Display system information and methodology"""
    
    st.markdown("""
    ## 🔍 Detection Methodology
    
    This system uses a transparent, rule-based approach with the following analysis modules:
    
    ### 🌐 Domain Analysis (0-35 points)
    - **Domain Age**: Recently registered domains (< 30 days) lose points
    - **Suspicious Patterns**: Multiple hyphens, excessive numbers, unusual character combinations
    - **TLD Risk Assessment**: High-risk top-level domains (.tk, .ml, .ga, etc.)
    
    ### 📝 Content Analysis (0-40 points) 
    - **Suspicious Keywords**: Urgent language, financial terminology, social engineering phrases
    - **Form Security**: Login forms without HTTPS encryption
    - **Content Quality**: Grammar, spelling, and professional presentation assessment
    
    ### 🔧 Technical Analysis (0-25 points)
    - **SSL Certificate**: Presence, validity, and issuer reputation
    - **DNS Configuration**: Unusual DNS patterns and hosting characteristics
    
    ## 📊 Scoring System
    
    - **0-39 points**: 🔴 **HIGH RISK** - Strong indicators of fraud/phishing
    - **40-69 points**: 🟡 **MEDIUM RISK** - Some suspicious indicators present  
    - **70-100 points**: 🟢 **LOW RISK** - Appears legitimate
    
    ## 🎯 Performance Targets
    
    - **Accuracy**: 75-80% on balanced test set
    - **Response Time**: 15-30 seconds per URL
    - **False Positive Rate**: < 5% for legitimate businesses
    
    ## 📚 Data Sources
    
    - **Phishing URLs**: PhishTank verified database
    - **Legitimate URLs**: Curated from reputable sources
    - **Real-time Analysis**: Direct website inspection and DNS queries
    """)

if __name__ == "__main__":
    main()