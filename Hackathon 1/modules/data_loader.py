"""
Data Loader Module
Handles downloading and preprocessing of training data from free sources
"""

import pandas as pd
import requests
import json
import os
from typing import List, Dict, Tuple
import time
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading and preprocessing of phishing and legitimate website datasets"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.phishtank_url = "http://data.phishtank.com/data/online-valid.json"
        self.legitimate_urls_file = os.path.join(data_dir, "legitimate_urls.txt")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
    
    def download_phishtank_data(self, max_samples: int = 10000) -> pd.DataFrame:
        """Download phishing URLs from PhishTank"""
        
        phishtank_file = os.path.join(self.data_dir, "phishtank_data.json")
        
        # Check if we already have the data
        if os.path.exists(phishtank_file):
            logger.info("Loading existing PhishTank data...")
            with open(phishtank_file, 'r') as f:
                data = json.load(f)
        else:
            logger.info("Downloading PhishTank data...")
            try:
                response = requests.get(self.phishtank_url, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                # Save data for future use
                with open(phishtank_file, 'w') as f:
                    json.dump(data, f)
                    
                logger.info(f"Downloaded {len(data)} phishing URLs from PhishTank")
                
            except Exception as e:
                logger.error(f"Failed to download PhishTank data: {e}")
                return pd.DataFrame()
        
        # Convert to DataFrame and sample if needed
        df = pd.DataFrame(data)
        if len(df) > max_samples:
            df = df.sample(n=max_samples, random_state=42)
            logger.info(f"Sampled {max_samples} phishing URLs")
        
        # Clean and prepare data
        df['label'] = 'phishing'
        df['url'] = df['url'].astype(str)
        
        return df[['url', 'label']].copy()
    
    def get_legitimate_urls(self, max_samples: int = 6000) -> pd.DataFrame:
        """Get legitimate URLs from various sources"""
        
        legitimate_urls = []
        
        # Top websites from multiple categories
        top_sites = [
            # Major tech companies
            "https://www.google.com", "https://www.microsoft.com", "https://www.apple.com",
            "https://www.amazon.com", "https://www.facebook.com", "https://www.twitter.com",
            "https://www.linkedin.com", "https://www.instagram.com", "https://www.youtube.com",
            "https://www.netflix.com", "https://www.spotify.com", "https://www.adobe.com",
            
            # Financial institutions
            "https://www.chase.com", "https://www.bankofamerica.com", "https://www.wellsfargo.com",
            "https://www.citibank.com", "https://www.usbank.com", "https://www.capitalone.com",
            "https://www.americanexpress.com", "https://www.paypal.com", "https://www.visa.com",
            "https://www.mastercard.com",
            
            # E-commerce
            "https://www.ebay.com", "https://www.walmart.com", "https://www.target.com",
            "https://www.bestbuy.com", "https://www.homedepot.com", "https://www.lowes.com",
            "https://www.macys.com", "https://www.nordstrom.com", "https://www.costco.com",
            
            # News and media
            "https://www.cnn.com", "https://www.bbc.com", "https://www.nytimes.com",
            "https://www.washingtonpost.com", "https://www.reuters.com", "https://www.bloomberg.com",
            "https://www.wsj.com", "https://www.forbes.com", "https://www.techcrunch.com",
            
            # Government and education
            "https://www.usa.gov", "https://www.irs.gov", "https://www.cdc.gov",
            "https://www.fda.gov", "https://www.nasa.gov", "https://www.mit.edu",
            "https://www.harvard.edu", "https://www.stanford.edu", "https://www.ucla.edu",
            
            # International
            "https://www.bbc.co.uk", "https://www.guardian.co.uk", "https://www.github.com",
            "https://www.stackoverflow.com", "https://www.wikipedia.org", "https://www.reddit.com",
            "https://www.airbnb.com", "https://www.uber.com", "https://www.booking.com"
        ]
        
        legitimate_urls.extend(top_sites)
        
        # Add some variations and subdomains
        additional_urls = []
        base_domains = ["google", "microsoft", "apple", "amazon", "facebook", "twitter"]
        
        for domain in base_domains:
            additional_urls.extend([
                f"https://support.{domain}.com",
                f"https://developers.{domain}.com",
                f"https://help.{domain}.com",
                f"https://about.{domain}.com"
            ])
        
        legitimate_urls.extend(additional_urls)
        
        # Generate more legitimate URLs by adding common business patterns
        business_patterns = [
            "https://www.{}.com".format(name) for name in [
                "adobe", "salesforce", "oracle", "ibm", "cisco", "intel", "nvidia",
                "shopify", "square", "stripe", "zoom", "slack", "dropbox", "box",
                "atlassian", "hubspot", "mailchimp", "constant-contact", "godaddy",
                "bluehost", "hostgator", "wordpress", "wix", "squarespace"
            ]
        ]
        
        legitimate_urls.extend(business_patterns)
        
        # If we still need more URLs, add some educational and nonprofit sites
        if len(legitimate_urls) < max_samples:
            edu_sites = [
                f"https://www.{uni}.edu" for uni in [
                    "berkeley", "cornell", "yale", "princeton", "columbia", "upenn",
                    "brown", "dartmouth", "northwestern", "duke", "vanderbilt"
                ]
            ]
            
            nonprofit_sites = [
                "https://www.redcross.org", "https://www.unitedway.org", "https://www.goodwill.org",
                "https://www.salvationarmy.org", "https://www.habitat.org", "https://www.wwf.org",
                "https://www.oxfam.org", "https://www.doctorswithoutborders.org"
            ]
            
            legitimate_urls.extend(edu_sites)
            legitimate_urls.extend(nonprofit_sites)
        
        # Sample if we have too many
        if len(legitimate_urls) > max_samples:
            import random
            random.seed(42)
            legitimate_urls = random.sample(legitimate_urls, max_samples)
        
        # Create DataFrame
        df = pd.DataFrame({
            'url': legitimate_urls,
            'label': 'legitimate'
        })
        
        logger.info(f"Generated {len(df)} legitimate URLs")
        
        return df
    
    def load_training_data(self, phishing_samples: int = 10000, legitimate_samples: int = 6000) -> pd.DataFrame:
        """Load and combine training data from all sources"""
        
        logger.info("Loading training data...")
        
        # Load phishing data
        phishing_df = self.download_phishtank_data(max_samples=phishing_samples)
        
        # Load legitimate data  
        legitimate_df = self.get_legitimate_urls(max_samples=legitimate_samples)
        
        # Combine datasets
        if len(phishing_df) > 0 and len(legitimate_df) > 0:
            combined_df = pd.concat([phishing_df, legitimate_df], ignore_index=True)
            
            # Shuffle the data
            combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            logger.info(f"Combined dataset: {len(combined_df)} total samples")
            logger.info(f"Phishing: {len(phishing_df)}, Legitimate: {len(legitimate_df)}")
            
            return combined_df
        else:
            logger.error("Failed to load training data")
            return pd.DataFrame()
    
    def save_dataset(self, df: pd.DataFrame, filename: str = "training_data.csv"):
        """Save dataset to file"""
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Dataset saved to {filepath}")
        
    def load_dataset(self, filename: str = "training_data.csv") -> pd.DataFrame:
        """Load dataset from file"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            logger.info(f"Dataset loaded from {filepath}: {len(df)} samples")
            return df
        else:
            logger.warning(f"Dataset file not found: {filepath}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader()
    training_data = loader.load_training_data(phishing_samples=1000, legitimate_samples=500)
    
    if len(training_data) > 0:
        print(f"Successfully loaded {len(training_data)} samples")
        print(f"Label distribution:\n{training_data['label'].value_counts()}")
        
        # Save dataset
        loader.save_dataset(training_data)
    else:
        print("Failed to load training data")