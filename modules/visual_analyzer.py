"""
Visual Analyzer Module
Analyzes website logos and visual content for brand verification
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
import numpy as np
from PIL import Image
import requests
from bs4 import BeautifulSoup
import io
import hashlib

# Optional imports for deep learning (graceful degradation)
try:
    import torch
    import torchvision.transforms as transforms
    from torchvision.models import resnet18, ResNet18_Weights
    import faiss
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualAnalyzer:
    """Analyzes visual content and logos for brand verification"""
    
    def __init__(self, logo_database_path: str = "brand_logos", company_database=None):
        self.logo_database_path = logo_database_path
        self.company_database = company_database
        self.model = None
        self.index = None
        self.logo_metadata = {}
        
        # Image preprocessing pipeline
        self.transform = None
        
        # Brand mapping (logo filename -> expected domains)
        self.brand_domains = {
            'google.png': ['google.com', 'gmail.com', 'youtube.com', 'chrome.google.com'],
            'amazon.png': ['amazon.com', 'aws.amazon.com', 'amazon.co.uk'],
            'apple.png': ['apple.com', 'icloud.com', 'itunes.apple.com'],
            'microsoft.png': ['microsoft.com', 'outlook.com', 'xbox.com', 'office.com'],
            'paypal.png': ['paypal.com', 'paypal.me'],
            'facebook.png': ['facebook.com', 'instagram.com', 'whatsapp.com'],
            'netflix.png': ['netflix.com'],
            'spotify.png': ['spotify.com'],
            'twitter.png': ['twitter.com', 'x.com'],
            'linkedin.png': ['linkedin.com'],
            'ebay.png': ['ebay.com'],
            'chase.png': ['chase.com'],
            'bankofamerica.png': ['bankofamerica.com'],
            'wellsfargo.png': ['wellsfargo.com'],
            'hp.png': ['hp.com', 'hpe.com'],
            'instagram.png': ['instagram.com', 'facebook.com']
        }
        
        if DEEP_LEARNING_AVAILABLE:
            self._initialize_model()
            self._setup_logo_database()
        else:
            logger.warning("⚠️ Deep learning libraries not available - visual analysis disabled")
    
    def _initialize_model(self):
        """Initialize ResNet18 model for feature extraction"""
        try:
            # Load pre-trained ResNet18
            self.model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
            
            # Remove the final classification layer to get features
            self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
            self.model.eval()
            
            # Setup image preprocessing
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            logger.info("✅ ResNet18 model initialized for feature extraction")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ResNet18 model: {e}")
            self.model = None
    
    def _setup_logo_database(self):
        """Setup FAISS index from logo database"""
        try:
            if not os.path.exists(self.logo_database_path):
                os.makedirs(self.logo_database_path)
                logger.info(f"📁 Created logo database directory: {self.logo_database_path}")
            
            # Load existing logos and build FAISS index
            logo_files = [f for f in os.listdir(self.logo_database_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            
            if not logo_files:
                logger.warning("⚠️ No logo files found in database - logo matching will be limited")
                return
            
            # Extract features from all logos
            features = []
            metadata = []
            
            for logo_file in logo_files:
                logo_path = os.path.join(self.logo_database_path, logo_file)
                try:
                    feature_vector = self._extract_features_from_path(logo_path)
                    if feature_vector is not None:
                        features.append(feature_vector)
                        metadata.append({
                            'filename': logo_file,
                            'brand': logo_file.split('.')[0],
                            'path': logo_path,
                            'domains': self.brand_domains.get(logo_file, [])
                        })
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process logo {logo_file}: {e}")
            
            if features:
                # Build FAISS index
                features_array = np.vstack(features).astype('float32')
                
                # L2 normalization for cosine similarity
                faiss.normalize_L2(features_array)
                
                # Create FAISS index
                dimension = features_array.shape[1]
                self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                self.index.add(features_array)
                
                self.logo_metadata = {i: metadata[i] for i in range(len(metadata))}
                
                logger.info(f"✅ FAISS index built with {len(features)} logo features")
            else:
                logger.warning("⚠️ No valid logo features extracted - logo matching disabled")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup logo database: {e}")
            self.index = None
    
    def _extract_features_from_path(self, image_path: str) -> Optional[np.ndarray]:
        """Extract features from image file path"""
        try:
            image = Image.open(image_path).convert('RGB')
            return self._extract_features_from_image(image)
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract features from {image_path}: {e}")
            return None
    
    def _extract_features_from_image(self, image: Image.Image) -> Optional[np.ndarray]:
        """Extract features from PIL Image using ResNet18"""
        try:
            if self.model is None or self.transform is None:
                return None
            
            # Preprocess image
            input_tensor = self.transform(image).unsqueeze(0)
            
            # Extract features
            with torch.no_grad():
                features = self.model(input_tensor)
                # Flatten and normalize
                features = features.view(features.size(0), -1)
                features = features.numpy().astype('float32')
                
                # L2 normalization
                features = features / np.linalg.norm(features, axis=1, keepdims=True)
                
                return features[0]
                
        except Exception as e:
            logger.warning(f"⚠️ Feature extraction failed: {e}")
            return None
    
    def _find_logos_on_page(self, soup: BeautifulSoup, base_url: str) -> List[Image.Image]:
        """Find and download logo images from webpage"""
        logos = []
        
        try:
            # Common logo selectors
            logo_selectors = [
                'img[alt*="logo" i]',
                'img[src*="logo" i]',
                'img[class*="logo" i]',
                'img[id*="logo" i]',
                '.logo img',
                '#logo img',
                'header img',
                '.header img',
                '.navbar img',
                '.nav img'
            ]
            
            found_images = set()
            
            # Find potential logo images
            for selector in logo_selectors:
                try:
                    elements = soup.select(selector)
                    for img in elements:
                        src = img.get('src')
                        if src:
                            # Convert relative URLs to absolute
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                parsed_base = urlparse(base_url)
                                src = f"{parsed_base.scheme}://{parsed_base.netloc}{src}"
                            elif not src.startswith('http'):
                                src = urljoin(base_url, src)
                            
                            found_images.add(src)
                except:
                    continue
            
            # Download and process images
            for img_url in list(found_images)[:5]:  # Limit to 5 images
                try:
                    response = requests.get(img_url, timeout=10, stream=True)
                    response.raise_for_status()
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        continue
                    
                    # Check file size (max 2MB)
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > 2 * 1024 * 1024:
                        continue
                    
                    # Load image
                    image_data = response.content
                    if len(image_data) > 2 * 1024 * 1024:  # 2MB limit
                        continue
                    
                    image = Image.open(io.BytesIO(image_data)).convert('RGB')
                    
                    # Filter by size (logos are typically small to medium)
                    width, height = image.size
                    if 20 <= width <= 500 and 20 <= height <= 500:
                        logos.append(image)
                    
                except Exception as e:
                    logger.debug(f"Failed to download logo from {img_url}: {e}")
                    continue
            
            logger.info(f"📷 Found {len(logos)} potential logo images")
            
        except Exception as e:
            logger.warning(f"⚠️ Logo detection failed: {e}")
        
        return logos
    
    def _match_logo_against_database(self, logo_image: Image.Image) -> List[Dict]:
        """Match logo against database using FAISS similarity search"""
        try:
            if self.index is None or self.model is None:
                return []
            
            # Extract features from input logo
            query_features = self._extract_features_from_image(logo_image)
            if query_features is None:
                return []
            
            # Search for similar logos
            query_features = query_features.reshape(1, -1).astype('float32')
            faiss.normalize_L2(query_features)
            
            # Search for top 5 similar logos
            similarities, indices = self.index.search(query_features, min(5, self.index.ntotal))
            
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx >= 0 and idx in self.logo_metadata:
                    metadata = self.logo_metadata[idx]
                    results.append({
                        'rank': i + 1,
                        'similarity': float(similarity),
                        'brand': metadata['brand'],
                        'filename': metadata['filename'],
                        'domains': metadata['domains'],
                        'confidence': 'High' if similarity > 0.8 else 'Medium' if similarity > 0.6 else 'Low'
                    })
            
            return results
            
        except Exception as e:
            logger.warning(f"⚠️ Logo matching failed: {e}")
            return []
    
    def analyze_visual_content(self, url: str, uploaded_logo: Optional[Image.Image] = None) -> Dict:
        """Perform comprehensive visual content analysis"""
        
        if not DEEP_LEARNING_AVAILABLE:
            return {
                'url': url,
                'score': 0,
                'explanations': [],
                'warnings': [{
                    'type': 'warning',
                    'category': 'visual_analysis',
                    'description': 'Visual Analysis Unavailable',
                    'evidence': 'Required libraries (torch, torchvision, faiss) not installed',
                    'module': 'Visual Analysis',
                    'recommendation': 'Install: pip install torch torchvision faiss-cpu'
                }],
                'logo_matches': [],
                'brand_verification': {'status': 'disabled', 'reason': 'Libraries not available'}
            }
        
        results = {
            'url': url,
            'score': 0,
            'explanations': [],
            'warnings': [],
            'logo_matches': [],
            'brand_verification': {'status': 'no_analysis', 'reason': 'No logos analyzed'}
        }
        
        try:
            # Extract domain for brand verification
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            logos_to_analyze = []
            
            # Add uploaded logo if provided
            if uploaded_logo:
                logos_to_analyze.append(('uploaded', uploaded_logo))
                logger.info("📤 Using uploaded logo for analysis")
            
            # Extract logos from webpage
            try:
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                page_logos = self._find_logos_on_page(soup, url)
                
                for i, logo in enumerate(page_logos):
                    logos_to_analyze.append((f'page_logo_{i+1}', logo))
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract logos from page: {e}")
                results['warnings'].append({
                    'type': 'warning',
                    'category': 'visual_extraction',
                    'description': 'Logo Extraction Failed',
                    'evidence': f'Could not extract logos from page: {str(e)[:100]}',
                    'module': 'Visual Analysis',
                    'recommendation': 'Upload logo manually for analysis'
                })
            
            # Analyze each logo
            all_matches = []
            best_brand_match = None
            highest_similarity = 0
            
            for logo_source, logo_image in logos_to_analyze:
                try:
                    matches = self._match_logo_against_database(logo_image)
                    
                    for match in matches:
                        match['source'] = logo_source
                        all_matches.append(match)
                        
                        # Track best match for brand verification
                        if match['similarity'] > highest_similarity:
                            highest_similarity = match['similarity']
                            best_brand_match = match
                            
                except Exception as e:
                    logger.warning(f"⚠️ Logo analysis failed for {logo_source}: {e}")
            
            results['logo_matches'] = all_matches
            
            # Brand verification analysis
            if best_brand_match:
                brand_verification = self._verify_brand_match(domain, best_brand_match)
                results['brand_verification'] = brand_verification
                
                # Score based on brand verification
                if brand_verification['status'] == 'mismatch':
                    points = -15 if highest_similarity > 0.8 else -10
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': f'Brand logo mismatch detected',
                        'points': abs(points),
                        'evidence': brand_verification['reason']
                    })
                elif brand_verification['status'] == 'match':
                    points = 8
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'positive',
                        'description': f'Brand logo verified',
                        'points': points,
                        'evidence': brand_verification['reason']
                    })
                elif brand_verification['status'] == 'uncertain':
                    results['explanations'].append({
                        'type': 'neutral',
                        'description': f'Brand verification uncertain',
                        'evidence': brand_verification['reason']
                    })
            else:
                results['brand_verification'] = {
                    'status': 'no_logos', 
                    'reason': 'No logos found or analyzed successfully'
                }
                
                # No logos found could be suspicious for certain domains
                if any(brand in domain for brand in ['bank', 'paypal', 'amazon', 'google', 'microsoft']):
                    points = -5
                    results['score'] += points
                    results['explanations'].append({
                        'type': 'negative',
                        'description': 'Expected brand logo missing',
                        'points': abs(points),
                        'evidence': f'No recognizable logos found for {domain}'
                    })
            
            # Summary information
            if all_matches:
                results['explanations'].append({
                    'type': 'neutral',
                    'description': f'Logo analysis completed',
                    'evidence': f'Found {len(all_matches)} logo matches across {len(logos_to_analyze)} images'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Visual analysis failed for {url}: {e}")
            return {
                'url': url,
                'score': 0,
                'explanations': [{
                    'type': 'neutral',
                    'description': 'Visual analysis error',
                    'evidence': f'Analysis failed: {str(e)[:100]}'
                }],
                'warnings': [],
                'logo_matches': [],
                'brand_verification': {'status': 'error', 'reason': str(e)[:100]}
            }
    
    def _verify_brand_match(self, domain: str, best_match: Dict) -> Dict:
        """Verify if detected brand matches the domain using database + hardcoded mappings"""
        try:
            brand = best_match['brand'].lower()
            similarity = best_match['similarity']
            expected_domains = best_match.get('domains', [])
            
            # Remove www prefix for comparison
            clean_domain = domain.replace('www.', '')
            
            # First check against hardcoded mappings (fast)
            # Check exact domain match
            if clean_domain in expected_domains:
                return {
                    'status': 'match',
                    'confidence': 'High' if similarity > 0.8 else 'Medium',
                    'reason': f'{brand.title()} logo matches domain {clean_domain} (similarity: {similarity:.3f})',
                    'brand': brand,
                    'similarity': similarity,
                    'source': 'hardcoded_mapping'
                }
            
            # Check partial domain match (subdomain)
            for expected_domain in expected_domains:
                if expected_domain in clean_domain or clean_domain in expected_domain:
                    return {
                        'status': 'match',
                        'confidence': 'Medium',
                        'reason': f'{brand.title()} logo matches domain family (similarity: {similarity:.3f})',
                        'brand': brand,
                        'similarity': similarity,
                        'source': 'hardcoded_mapping'
                    }
            
            # Check against company database if available
            if self.company_database and hasattr(self.company_database, 'get_company_by_domain'):
                company_info = self.company_database.get_company_by_domain(domain)
                if company_info:
                    company_name = company_info.get('name', '').lower()
                    
                    # Check if brand name appears in company name
                    if brand in company_name or company_name in brand:
                        return {
                            'status': 'match',
                            'confidence': 'High' if similarity > 0.8 else 'Medium',
                            'reason': f'{brand.title()} logo matches company "{company_info.get("name", "")}" (similarity: {similarity:.3f})',
                            'brand': brand,
                            'similarity': similarity,
                            'source': 'company_database',
                            'company_info': company_info
                        }
                    
                    # Check for brand-related industries (for generic brands)
                    industry = company_info.get('industry', '').lower()
                    if brand in ['hp', 'microsoft'] and 'technology' in industry:
                        return {
                            'status': 'uncertain',
                            'confidence': 'Medium',
                            'reason': f'{brand.title()} logo found, company in tech industry but name mismatch (similarity: {similarity:.3f})',
                            'brand': brand,
                            'similarity': similarity,
                            'source': 'company_database',
                            'company_info': company_info
                        }
            
            # Brand name in domain but not verified
            if brand in clean_domain:
                return {
                    'status': 'uncertain',
                    'confidence': 'Low',
                    'reason': f'{brand.title()} logo found but domain not in verified list (similarity: {similarity:.3f})',
                    'brand': brand,
                    'similarity': similarity,
                    'source': 'domain_analysis'
                }
            
            # Complete mismatch - logo doesn't match domain
            return {
                'status': 'mismatch',
                'confidence': 'High' if similarity > 0.8 else 'Medium',
                'reason': f'{brand.title()} logo detected but domain is {clean_domain} (similarity: {similarity:.3f})',
                'brand': brand,
                'similarity': similarity,
                'expected_domains': expected_domains,
                'source': 'mismatch_detection'
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Brand verification failed: {e}")
            return {
                'status': 'error',
                'reason': f'Brand verification error: {str(e)[:100]}'
            }
    
    def add_logo_to_database(self, logo_image: Image.Image, brand_name: str, 
                           associated_domains: List[str]) -> bool:
        """Add a new logo to the database"""
        try:
            if not DEEP_LEARNING_AVAILABLE:
                logger.warning("⚠️ Cannot add logo - deep learning libraries not available")
                return False
            
            # Create filename
            filename = f"{brand_name.lower().replace(' ', '_')}.png"
            logo_path = os.path.join(self.logo_database_path, filename)
            
            # Save image
            logo_image.save(logo_path, 'PNG')
            
            # Update brand domains mapping
            self.brand_domains[filename] = associated_domains
            
            # Rebuild index
            self._setup_logo_database()
            
            logger.info(f"✅ Added {brand_name} logo to database")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add logo to database: {e}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the logo database"""
        try:
            if not os.path.exists(self.logo_database_path):
                return {'status': 'no_database', 'logo_count': 0, 'brands': []}
            
            logo_files = [f for f in os.listdir(self.logo_database_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            
            brands = [f.split('.')[0].replace('_', ' ').title() for f in logo_files]
            
            return {
                'status': 'available' if DEEP_LEARNING_AVAILABLE else 'libraries_missing',
                'logo_count': len(logo_files),
                'brands': brands,
                'database_path': self.logo_database_path,
                'index_status': 'ready' if self.index is not None else 'not_initialized'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

# Helper function to safely import visual analyzer
def create_visual_analyzer(logo_database_path: str = "brand_logos", company_database=None) -> Optional['VisualAnalyzer']:
    """Create visual analyzer with graceful degradation"""
    try:
        return VisualAnalyzer(logo_database_path, company_database)
    except Exception as e:
        logger.warning(f"⚠️ Visual analyzer creation failed: {e}")
        return None

if __name__ == "__main__":
    # Test the visual analyzer
    analyzer = create_visual_analyzer()
    
    if analyzer:
        # Get database stats
        stats = analyzer.get_database_stats()
        print(f"Database status: {stats}")
        
        # Test with a sample URL (if visual analysis is available)
        if DEEP_LEARNING_AVAILABLE:
            test_url = "https://www.google.com"
            print(f"\nTesting visual analysis: {test_url}")
            result = analyzer.analyze_visual_content(test_url)
            print(f"Visual analysis result: {result}")
    else:
        print("Visual analyzer not available")