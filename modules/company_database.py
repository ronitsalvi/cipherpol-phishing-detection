"""
Company Database Module
Processes large JSON company dataset and provides whitelist functionality
"""

import json
import sqlite3
import os
import logging
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
import time
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompanyDatabase:
    """Manages company database and website whitelist functionality"""
    
    def __init__(self, database_path: str = "Database/Free Company Dataset", 
                 cache_db_path: str = "company_cache.db"):
        self.database_path = database_path
        self.cache_db_path = cache_db_path
        self.whitelist_domains = set()
        self.company_lookup = {}
        self.is_loaded = False
        self.loading_in_progress = False
        self.load_progress = 0
        
        # Domain normalization patterns
        self.domain_prefixes = ['www.', 'api.', 'mail.', 'support.', 'help.', 'blog.', 'shop.', 'store.']
        
        # Initialize database
        self._init_cache_db()
        
        # Start background loading if dataset exists
        if os.path.exists(self.database_path):
            self._start_background_loading()
        else:
            logger.warning(f"⚠️ Company dataset not found at: {self.database_path}")
    
    def _init_cache_db(self):
        """Initialize SQLite cache database for fast lookups"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Create companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    website TEXT,
                    normalized_domain TEXT,
                    industry TEXT,
                    founded INTEGER,
                    size TEXT,
                    locality TEXT,
                    region TEXT,
                    country TEXT,
                    linkedin_url TEXT,
                    has_logo BOOLEAN DEFAULT 0,
                    logo_path TEXT
                )
            ''')
            
            # Create index on normalized_domain for fast lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_normalized_domain 
                ON companies(normalized_domain)
            ''')
            
            # Create domains table for fast whitelist checking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist_domains (
                    domain TEXT PRIMARY KEY,
                    company_id TEXT,
                    company_name TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_whitelist_domain 
                ON whitelist_domains(domain)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ SQLite cache database initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize cache database: {e}")
    
    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain for consistent matching"""
        if not domain:
            return ""
        
        # Remove protocol
        if '://' in domain:
            domain = domain.split('://', 1)[1]
        
        # Remove path and query parameters
        domain = domain.split('/')[0].split('?')[0].split('#')[0]
        
        # Convert to lowercase
        domain = domain.lower().strip()
        
        # Remove common prefixes
        for prefix in self.domain_prefixes:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
                break
        
        return domain
    
    def _start_background_loading(self):
        """Start background loading of company database"""
        if self.loading_in_progress or self.is_loaded:
            return
        
        # Check if cache is already built and recent
        if self._is_cache_valid():
            self._load_from_cache()
            return
        
        # Start background loading thread
        self.loading_in_progress = True
        thread = threading.Thread(target=self._process_company_dataset, daemon=True)
        thread.start()
        logger.info("🔄 Started background loading of company database...")
    
    def _is_cache_valid(self) -> bool:
        """Check if SQLite cache is valid and recent"""
        try:
            if not os.path.exists(self.cache_db_path):
                return False
            
            # Check if cache file is newer than dataset
            cache_mtime = os.path.getmtime(self.cache_db_path)
            dataset_mtime = os.path.getmtime(self.database_path)
            
            if cache_mtime > dataset_mtime:
                # Check if cache has data
                conn = sqlite3.connect(self.cache_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM companies WHERE website IS NOT NULL")
                count = cursor.fetchone()[0]
                conn.close()
                
                if count > 1000:  # Reasonable threshold
                    logger.info(f"✅ Using existing cache with {count} companies")
                    return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Cache validation failed: {e}")
            return False
    
    def _load_from_cache(self):
        """Load whitelist from existing cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Load whitelist domains
            cursor.execute("SELECT domain FROM whitelist_domains")
            domains = cursor.fetchall()
            self.whitelist_domains = {row[0] for row in domains}
            
            # Load company lookup
            cursor.execute("""
                SELECT normalized_domain, name, industry, website, has_logo, logo_path
                FROM companies WHERE website IS NOT NULL
            """)
            companies = cursor.fetchall()
            
            for domain, name, industry, website, has_logo, logo_path in companies:
                self.company_lookup[domain] = {
                    'name': name,
                    'industry': industry,
                    'website': website,
                    'has_logo': bool(has_logo),
                    'logo_path': logo_path
                }
            
            conn.close()
            
            self.is_loaded = True
            logger.info(f"✅ Loaded {len(self.whitelist_domains)} domains from cache")
            
        except Exception as e:
            logger.error(f"❌ Failed to load from cache: {e}")
    
    def _process_company_dataset(self):
        """Process the large JSON dataset in chunks"""
        try:
            logger.info("🔄 Processing company dataset...")
            processed_count = 0
            valid_websites = 0
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("DELETE FROM companies")
            cursor.execute("DELETE FROM whitelist_domains")
            
            with open(self.database_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file):
                    try:
                        # Parse JSON record
                        record = json.loads(line.strip())
                        website = record.get('website')
                        
                        if website and website.strip():
                            normalized_domain = self._normalize_domain(website)
                            
                            if normalized_domain:
                                # Insert into companies table
                                cursor.execute('''
                                    INSERT OR REPLACE INTO companies 
                                    (id, name, website, normalized_domain, industry, founded, 
                                     size, locality, region, country, linkedin_url)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    record.get('id', ''),
                                    record.get('name', ''),
                                    website,
                                    normalized_domain,
                                    record.get('industry', ''),
                                    record.get('founded'),
                                    record.get('size', ''),
                                    record.get('locality', ''),
                                    record.get('region', ''),
                                    record.get('country', ''),
                                    record.get('linkedin_url', '')
                                ))
                                
                                # Add to whitelist
                                cursor.execute('''
                                    INSERT OR REPLACE INTO whitelist_domains 
                                    (domain, company_id, company_name)
                                    VALUES (?, ?, ?)
                                ''', (normalized_domain, record.get('id', ''), record.get('name', '')))
                                
                                valid_websites += 1
                                self.whitelist_domains.add(normalized_domain)
                                self.company_lookup[normalized_domain] = {
                                    'name': record.get('name', ''),
                                    'industry': record.get('industry', ''),
                                    'website': website,
                                    'has_logo': False,
                                    'logo_path': None
                                }
                        
                        processed_count += 1
                        
                        # Commit in batches and update progress
                        if processed_count % 10000 == 0:
                            conn.commit()
                            self.load_progress = (line_num / 32330231) * 100
                            logger.info(f"📊 Processed {processed_count:,} records, {valid_websites:,} valid websites ({self.load_progress:.1f}%)")
                        
                        # Memory management
                        if processed_count % 100000 == 0:
                            import gc
                            gc.collect()
                    
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        if processed_count % 50000 == 0:  # Log occasional errors
                            logger.debug(f"Record processing error: {e}")
                        continue
            
            conn.commit()
            conn.close()
            
            self.is_loaded = True
            self.loading_in_progress = False
            self.load_progress = 100
            
            logger.info(f"✅ Database loading complete: {valid_websites:,} companies with websites loaded")
            
        except Exception as e:
            logger.error(f"❌ Dataset processing failed: {e}")
            self.loading_in_progress = False
    
    def is_domain_whitelisted(self, url: str) -> Tuple[bool, Optional[Dict]]:
        """Check if domain is in whitelist (fast O(1) lookup)"""
        try:
            normalized_domain = self._normalize_domain(url)
            
            if normalized_domain in self.whitelist_domains:
                company_info = self.company_lookup.get(normalized_domain, {})
                return True, {
                    'status': 'whitelisted',
                    'company_name': company_info.get('name', 'Unknown'),
                    'industry': company_info.get('industry', 'Unknown'),
                    'website': company_info.get('website', ''),
                    'source': 'company_database'
                }
            
            return False, None
            
        except Exception as e:
            logger.debug(f"Whitelist check failed for {url}: {e}")
            return False, None
    
    def search_companies(self, query: str, limit: int = 10) -> List[Dict]:
        """Search companies by name or domain"""
        try:
            if not self.is_loaded:
                return []
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Search by name or domain
            cursor.execute('''
                SELECT name, website, normalized_domain, industry, country
                FROM companies 
                WHERE (name LIKE ? OR normalized_domain LIKE ?) 
                AND website IS NOT NULL
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': row[0],
                    'website': row[1], 
                    'domain': row[2],
                    'industry': row[3],
                    'country': row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Company search failed: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics and loading status"""
        try:
            stats = {
                'is_loaded': self.is_loaded,
                'loading_in_progress': self.loading_in_progress,
                'load_progress': self.load_progress,
                'whitelist_count': len(self.whitelist_domains),
                'cache_exists': os.path.exists(self.cache_db_path)
            }
            
            if self.is_loaded:
                conn = sqlite3.connect(self.cache_db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM companies WHERE website IS NOT NULL")
                total_companies = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT industry) FROM companies WHERE industry IS NOT NULL")
                total_industries = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM companies WHERE has_logo = 1")
                companies_with_logos = cursor.fetchone()[0]
                
                conn.close()
                
                stats.update({
                    'total_companies': total_companies,
                    'total_industries': total_industries,
                    'companies_with_logos': companies_with_logos
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {
                'is_loaded': False,
                'loading_in_progress': False,
                'load_progress': 0,
                'error': str(e)
            }
    
    def update_company_logo(self, domain: str, logo_path: str) -> bool:
        """Update company record to indicate it has a logo"""
        try:
            if not self.is_loaded:
                return False
            
            normalized_domain = self._normalize_domain(domain)
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE companies 
                SET has_logo = 1, logo_path = ?
                WHERE normalized_domain = ?
            ''', (logo_path, normalized_domain))
            
            conn.commit()
            conn.close()
            
            # Update in-memory lookup
            if normalized_domain in self.company_lookup:
                self.company_lookup[normalized_domain]['has_logo'] = True
                self.company_lookup[normalized_domain]['logo_path'] = logo_path
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update company logo: {e}")
            return False
    
    def get_company_by_domain(self, domain: str) -> Optional[Dict]:
        """Get company information by domain"""
        try:
            normalized_domain = self._normalize_domain(domain)
            return self.company_lookup.get(normalized_domain)
        except Exception as e:
            logger.debug(f"Company lookup failed for {domain}: {e}")
            return None
    
    def get_similar_domains(self, domain: str, limit: int = 5) -> List[Dict]:
        """Find similar domains in database (for typosquatting detection)"""
        try:
            if not self.is_loaded:
                return []
            
            from difflib import SequenceMatcher
            normalized_domain = self._normalize_domain(domain)
            
            similar_domains = []
            
            # Check against known domains
            for db_domain in list(self.whitelist_domains)[:10000]:  # Limit search scope
                if abs(len(db_domain) - len(normalized_domain)) <= 3:  # Similar length
                    ratio = SequenceMatcher(None, normalized_domain, db_domain).ratio()
                    if 0.7 < ratio < 0.95:  # Similar but not identical
                        company_info = self.company_lookup.get(db_domain, {})
                        similar_domains.append({
                            'domain': db_domain,
                            'similarity': ratio,
                            'company_name': company_info.get('name', 'Unknown'),
                            'industry': company_info.get('industry', 'Unknown')
                        })
            
            # Sort by similarity and return top matches
            similar_domains.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_domains[:limit]
            
        except Exception as e:
            logger.error(f"❌ Similar domain search failed: {e}")
            return []
    
    def force_reload(self):
        """Force reload the database from source"""
        try:
            if os.path.exists(self.cache_db_path):
                os.remove(self.cache_db_path)
            
            self.whitelist_domains.clear()
            self.company_lookup.clear()
            self.is_loaded = False
            self.load_progress = 0
            
            self._init_cache_db()
            self._start_background_loading()
            
            logger.info("🔄 Database reload initiated")
            
        except Exception as e:
            logger.error(f"❌ Database reload failed: {e}")

def create_company_database(database_path: str = "Database/Free Company Dataset") -> CompanyDatabase:
    """Create company database with error handling"""
    try:
        return CompanyDatabase(database_path)
    except Exception as e:
        logger.error(f"❌ Failed to create company database: {e}")
        # Return a dummy database that always returns False for whitelist checks
        class DummyDatabase:
            def is_domain_whitelisted(self, url): return False, None
            def get_database_stats(self): return {'is_loaded': False, 'error': str(e)}
            def search_companies(self, query, limit=10): return []
            def get_company_by_domain(self, domain): return None
            def get_similar_domains(self, domain, limit=5): return []
        
        return DummyDatabase()

if __name__ == "__main__":
    # Test the company database
    db = create_company_database()
    
    # Wait a moment for background loading
    time.sleep(2)
    
    # Test whitelist functionality
    test_domains = [
        "google.com",
        "microsoft.com", 
        "cyberette.ai",  # From sample data
        "roseburgradiologists.com",  # From sample data
        "fake-phishing-site.tk"
    ]
    
    for domain in test_domains:
        is_whitelisted, info = db.is_domain_whitelisted(domain)
        print(f"{domain}: {'✅ WHITELISTED' if is_whitelisted else '❌ Not in database'}")
        if info:
            print(f"   Company: {info.get('company_name', 'Unknown')}")
    
    # Show database stats
    stats = db.get_database_stats()
    print(f"\nDatabase Stats: {stats}")