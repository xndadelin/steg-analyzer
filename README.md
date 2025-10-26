<div align="center">
  <a href="https://moonshot.hackclub.com" target="_blank">
    <img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/35ad2be8c916670f3e1ac63c1df04d76a4b337d1_moonshot.png" 
         alt="This project is part of Moonshot, a 4-day hackathon in Florida visiting Kennedy Space Center and Universal Studios!" 
         style="width: 100%;">
  </a>
</div>

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
