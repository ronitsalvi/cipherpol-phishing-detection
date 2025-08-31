# Brand Logo Database

This folder contains reference logos for brand verification during phishing detection.

## Supported Brands

The system can verify logos for the following brands:

- Google (google.png) - google.com, gmail.com, youtube.com
- Amazon (amazon.png) - amazon.com, aws.amazon.com, amazon.co.uk
- Apple (apple.png) - apple.com, icloud.com, itunes.apple.com
- Microsoft (microsoft.png) - microsoft.com, outlook.com, xbox.com
- PayPal (paypal.png) - paypal.com, paypal.me
- Facebook (facebook.png) - facebook.com, instagram.com, whatsapp.com
- Netflix (netflix.png) - netflix.com
- Spotify (spotify.png) - spotify.com
- Twitter (twitter.png) - twitter.com, x.com
- LinkedIn (linkedin.png) - linkedin.com
- eBay (ebay.png) - ebay.com
- Chase Bank (chase.png) - chase.com
- Bank of America (bankofamerica.png) - bankofamerica.com
- Wells Fargo (wellsfargo.png) - wellsfargo.com

## Adding New Logos

1. Save logo images as PNG files in this folder
2. Use clear, descriptive filenames (e.g., `brandname.png`)
3. Update the `brand_domains` mapping in `visual_analyzer.py`
4. Restart the application to rebuild the FAISS index

## Image Requirements

- Format: PNG, JPG, JPEG, GIF, or BMP
- Size: 20x20 to 500x500 pixels
- File size: Under 2MB
- Clear, high-quality brand logos work best

## How It Works

1. **Feature Extraction**: Uses ResNet18 to extract visual features
2. **Similarity Search**: Uses FAISS for fast similarity matching
3. **Brand Verification**: Compares detected brand with domain
4. **Scoring**: Penalizes brand mismatches, rewards legitimate matches