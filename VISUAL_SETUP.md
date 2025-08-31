# Visual Analysis Setup Guide

## Overview

The visual analysis feature adds brand logo verification to the phishing detection system using computer vision and machine learning.

## Installation

### Option 1: Install Required Libraries

```bash
pip install torch torchvision faiss-cpu
```

### Option 2: Install from Requirements File

```bash
pip install -r requirements_visual.txt
```

### Option 3: CPU-Only Installation (Recommended for most users)

```bash
# Install PyTorch CPU version
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install FAISS CPU version
pip install faiss-cpu
```

## Features Enabled by Visual Analysis

1. **Logo Detection**: Automatically extracts logos from webpages
2. **Brand Verification**: Compares detected logos against known brand database
3. **Similarity Matching**: Uses ResNet18 + FAISS for accurate logo matching
4. **Brand Mismatch Detection**: Penalizes sites using logos that don't match their domain
5. **Manual Logo Upload**: Users can upload logos for verification

## How It Works

1. **Feature Extraction**: ResNet18 neural network extracts visual features from logos
2. **Database Indexing**: FAISS creates searchable index of reference brand logos
3. **Similarity Search**: Finds top 5 most similar logos with confidence scores
4. **Brand Verification**: Checks if detected brand matches the website's domain
5. **Scoring Integration**: Applies penalties (-15 points) for brand mismatches

## Logo Database

- Located in `brand_logos/` folder
- Supports PNG, JPG, JPEG, GIF, BMP formats
- Covers major brands: Google, Amazon, Apple, Microsoft, PayPal, Facebook, etc.
- Users can add new logos by placing files in the folder

## Graceful Degradation

- System works fully without visual analysis libraries
- Shows informational warnings when libraries are missing
- Visual analysis component shows "N/A" when disabled
- No impact on core phishing detection functionality

## Performance

- Visual analysis adds ~2-3 seconds to analysis time
- Uses 15% weight in final scoring (reduced from other components)
- Timeout protection prevents hanging on image processing
- Memory limits prevent resource exhaustion

## Testing

```bash
# Test visual analyzer creation
python3 -c "from modules.visual_analyzer import create_visual_analyzer; va = create_visual_analyzer(); print('Status:', va.get_database_stats())"

# Test full integration
python3 -c "from modules.robust_phishing_detector import RobustPhishingDetector; d = RobustPhishingDetector(); result = d.analyze_url_with_visual('https://www.google.com'); print('Visual component:', result['component_scores']['visual'])"
```

## Troubleshooting

### Libraries Not Installing
- Try using conda: `conda install pytorch torchvision faiss-cpu -c pytorch`
- Use CPU-only versions to avoid CUDA dependencies
- Check Python version compatibility (3.8+ recommended)

### Memory Issues
- Visual analysis has built-in memory limits
- Large images are automatically resized
- Database limited to reasonable number of logos

### Performance Issues
- Increase timeout settings in `robust_phishing_detector.py`
- Reduce logo database size
- Use smaller reference logo images