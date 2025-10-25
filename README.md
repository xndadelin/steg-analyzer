# ‼️ Steganography analysis web application

Hello! This is a Flask web application for analyzing images for hidden data and steganography.

## Features
- **binwalk** - extract hidden files/data
- **boremost** - recover files based on headers/footers
- **exiftool** - extract metadata
- **file** - identify file types
- **strings** - extract readable strings from the image
- **zsteg** - PNG/BMP steganography detection
- **pngcheck** - PNG integrity verification
- **image_filters** - grayscale, high contrat, edge detection, brightness, color inversion, sharpening

## Requirements to run it on your localhost
- python3
- docker

## Local setup
1. Clone the repo
```bash
git clone https://github.com/xndadelin/steg-analyzer && cd NXT
```
2. Build
```bash
docker build -t steg .
```
3. Run
```bash
docker run -p 5000:5000 steg
```