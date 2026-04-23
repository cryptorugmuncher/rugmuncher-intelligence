# Extension Icons

This directory contains the extension icons in various sizes required by Chrome/Firefox.

## Required Sizes

- `icon16.png` - Toolbar icon
- `icon32.png` - Toolbar icon (retina)
- `icon48.png` - Extension management page
- `icon128.png` - Chrome Web Store and installation

## Generating Icons

### Option 1: Use the provided SVG

If you have an SVG logo, convert it to PNG:

```bash
# Using Inkscape
inkscape logo.svg --export-filename=icon16.png -w 16 -h 16
inkscape logo.svg --export-filename=icon32.png -w 32 -h 32
inkscape logo.svg --export-filename=icon48.png -w 48 -h 48
inkscape logo.svg --export-filename=icon128.png -w 128 -h 128

# Using ImageMagick
convert logo.svg -resize 16x16 icon16.png
convert logo.svg -resize 32x32 icon32.png
convert logo.svg -resize 48x48 icon48.png
convert logo.svg -resize 128x128 icon128.png
```

### Option 2: Figma/Design Tool

Export your logo from Figma/Sketch/Adobe XD at the following sizes:
- 16x16 px
- 32x32 px
- 48x48 px
- 128x128 px

### Option 3: Online Generator

Use an online tool like:
- https://www.photopea.com/ (free Photoshop alternative)
- https://convertio.co/ (SVG to PNG converter)

## Icon Design Guidelines

1. **Use a simple, recognizable design** that works at small sizes
2. **Keep margins** - don't extend to the very edge of the canvas
3. **Use transparency** (PNG with alpha channel) for non-rectangular shapes
4. **Avoid text** - it won't be readable at 16x16
5. **Use the brand colors**: #8b5cf6 (primary purple)

## Example Icon (Base64 Placeholder)

You can use this temporary icon by creating a simple colored square:

```javascript
// Create a simple canvas-based icon for testing
const canvas = document.createElement('canvas');
canvas.width = 128;
canvas.height = 128;
const ctx = canvas.getContext('2d');

// Purple gradient background
const gradient = ctx.createLinearGradient(0, 0, 128, 128);
gradient.addColorStop(0, '#8b5cf6');
gradient.addColorStop(1, '#6d28d9');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 128, 128);

// Rounded corners
ctx.globalCompositeOperation = 'destination-in';
ctx.beginPath();
ctx.roundRect(0, 0, 128, 128, 24);
ctx.fill();

// Save as PNG
canvas.toBlob(blob => {
  const url = URL.createObjectURL(blob);
  // Download or use the URL
});
```

## Icon Placeholder

Until proper icons are generated, you can create a simple text file with this content saved as each icon file (this is NOT a valid PNG but serves as a placeholder):

```
PLACEHOLDER: Replace with actual 16x16 PNG
PLACEHOLDER: Replace with actual 32x32 PNG
PLACEHOLDER: Replace with actual 48x48 PNG
PLACEHOLDER: Replace with actual 128x128 PNG
```

**Note**: Chrome will show a default puzzle piece icon if the PNG files are missing or invalid.
