# Portrait Architecture

The **WaifuPuller-Profile** portrait rendering pipeline is designed to transform a static image into a high-fidelity, luxury ASCII art centerpiece using WebP technology.

## Core Philosophy
- **Manual Preparation:** The pipeline relies on a manually prepared, pre-cut transparent PNG.
- **Zero AI Segmentation:** We do NOT perform any automated background removal, subject extraction, or AI segmentation (e.g., `rembg`). The silhouette is strictly preserved from the source file.
- **Deterministic Quality:** The entire process is strictly controlled by a single configuration source (`config/portrait.yaml`).

## The Pipeline

1. **Source Ingestion:** Loads `assets/source-images/portrait.png`. Fails fast and explicitly if the image is missing.
2. **Preprocessing:**
   - Evaluates EXIF orientation.
   - Bounding-box automatic crop to trim any excess transparent padding.
   - Lanczos spatial resampling.
   - **Local Contrast Enhancement (CLAHE Approximation)** to boost shadow and highlight details before ASCII conversion.
   - **Adaptive Edge Enhancement** to sharpen silhouettes and internal lines.
3. **ASCII Generation:**
   - Maps spatial luminance to a configurable luxury character set (e.g., "WMB8&%#*+=-:. ").
   - Uses **Floyd-Steinberg Error Diffusion** dithering for smooth shading across intricate regions like eyes and hair.
4. **Raster Rendering:**
   - Encodes the ASCII matrix directly into a highly compressed, crisp WebP image.
   - Applies subtle bloom filter overlays for a premium terminal-glow aesthetic.
