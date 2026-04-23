#!/bin/bash

# Build script for Rug Munch Intel Browser Extension
# ==================================================

set -e

EXTENSION_NAME="rug-munch-intel"
VERSION="1.0.0"
BUILD_DIR="dist"

echo "🏗️  Building Rug Munch Intel Extension v${VERSION}..."

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

# Create build directory
mkdir -p "$BUILD_DIR"

# Copy manifest
echo "📋 Copying manifest..."
cp manifest.json "$BUILD_DIR/"

# Copy source files
echo "📁 Copying source files..."
cp -r src "$BUILD_DIR/"

# Copy icons (or create placeholder if missing)
echo "🎨 Setting up icons..."
if [ -d "icons" ]; then
    cp -r icons "$BUILD_DIR/"
else
    mkdir -p "$BUILD_DIR/icons"
    echo "⚠️  Warning: Icons directory not found. Using placeholders."
fi

# Copy sounds if they exist
if [ -d "sounds" ]; then
    echo "🔊 Copying sounds..."
    cp -r sounds "$BUILD_DIR/"
fi

# Copy README
cp README.md "$BUILD_DIR/"

# Validate JSON
echo "✅ Validating manifest.json..."
if ! python3 -c "import json; json.load(open('$BUILD_DIR/manifest.json'))" 2>/dev/null; then
    echo "❌ Error: manifest.json is not valid JSON"
    exit 1
fi

# Create zip for Chrome Web Store
echo "📦 Creating Chrome Web Store package..."
cd "$BUILD_DIR"
zip -r "../${EXTENSION_NAME}-${VERSION}.zip" . -x "*.DS_Store" -x "*.git*"
cd ..

# Calculate sizes
echo ""
echo "📊 Build Statistics:"
echo "==================="
echo "Extension folder size: $(du -sh "$BUILD_DIR" | cut -f1)"
echo "Zip package size: $(du -sh "${EXTENSION_NAME}-${VERSION}.zip" | cut -f1)"

# Count files
FILE_COUNT=$(find "$BUILD_DIR" -type f | wc -l)
echo "Total files: $FILE_COUNT"

echo ""
echo "✨ Build complete!"
echo ""
echo "Next steps:"
echo "1. Test the extension:"
echo "   - Open Chrome and go to chrome://extensions/"
echo "   - Enable 'Developer mode'"
echo "   - Click 'Load unpacked' and select the '$BUILD_DIR' folder"
echo ""
echo "2. For Chrome Web Store submission:"
echo "   - Upload: ${EXTENSION_NAME}-${VERSION}.zip"
echo "   - Or use: $BUILD_DIR folder for testing"
echo ""
echo "3. To generate icons:"
echo "   - Create icons/ folder with icon16.png, icon32.png, icon48.png, icon128.png"
echo "   - Or run: ./generate-icons.sh (if available)"
echo ""
