#!/bin/bash

# 🚀 FarmyGo Courier App - Setup Script
echo "🚀 Setting up FarmyGo Courier App..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found. Please run this script from the courier-app directory.${NC}"
    exit 1
fi

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

# Check if EAS CLI is installed
if ! command -v eas &> /dev/null; then
    echo -e "${YELLOW}⚠️  EAS CLI not found. Installing...${NC}"
    npm install -g eas-cli
fi

# Create assets directory if it doesn't exist
echo -e "${BLUE}📁 Creating assets directory...${NC}"
mkdir -p assets

# Create placeholder icons if they don't exist
if [ ! -f "assets/icon.png" ]; then
    echo -e "${YELLOW}⚠️  Creating placeholder icon...${NC}"
    # Create a simple 1024x1024 colored square as placeholder
    # In production, replace with actual FarmyGo logo
    echo "ℹ️  Please replace assets/icon.png with the actual FarmyGo logo (1024x1024 PNG)"
fi

# Create placeholder splash screen
if [ ! -f "assets/splash.png" ]; then
    echo -e "${YELLOW}⚠️  Creating placeholder splash screen...${NC}"
    echo "ℹ️  Please replace assets/splash.png with the actual FarmyGo splash screen (1284x2778 PNG)"
fi

# Create .env file for local development
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️  Creating .env file...${NC}"
    cat > .env << EOL
# FarmyGo Courier App - Development Environment
API_URL=http://localhost:8001/api
EXPO_PUBLIC_API_URL=http://localhost:8001/api

# For production, update to:
# API_URL=https://farmygo.ch/api
# EXPO_PUBLIC_API_URL=https://farmygo.ch/api
EOL
fi

# Show next steps
echo -e "${GREEN}✅ Setup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Replace placeholder assets with actual FarmyGo branding:"
echo "   - assets/icon.png (1024x1024)"
echo "   - assets/splash.png (1284x2778)"
echo "   - assets/adaptive-icon.png (1024x1024)"
echo ""
echo "2. Start development server:"
echo -e "   ${GREEN}npx expo start${NC}"
echo ""
echo "3. Test on your device:"
echo "   - Install Expo Go app"
echo "   - Scan QR code from terminal"
echo ""
echo "4. Build for production:"
echo -e "   ${GREEN}eas build --platform all --profile production${NC}"
echo ""
echo "5. Submit to stores:"
echo -e "   ${GREEN}eas submit --platform all --profile production${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Make sure your backend is running on http://localhost:8001 for local testing${NC}"
echo -e "${YELLOW}💡 For production builds, update API_URL in app.json to https://farmygo.ch/api${NC}"
echo ""
echo -e "${GREEN}🎉 Happy coding!${NC}"