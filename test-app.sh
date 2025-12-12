#!/bin/bash

# SmartBudget Mobile App Test Script
# This script helps test the mobile app functionality

echo "🚀 SmartBudget Mobile App Test Script"
echo "====================================="

# Check if we're in the mobile directory
if [ ! -f "package.json" ] || [ ! -d "src" ]; then
    echo "❌ Error: Please run this script from the mobile directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please create it from the example:"
    echo "   cp .env.example .env"
    exit 1
fi

echo "✅ Environment check passed"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
fi

echo "✅ Dependencies check passed"

# Check if Expo CLI is installed
if ! command -v expo &> /dev/null; then
    echo "❌ Error: Expo CLI not found. Please install it:"
    echo "   npm install -g @expo/cli"
    exit 1
fi

echo "✅ Expo CLI check passed"

# Check environment variables
echo "🔍 Checking environment variables..."

# Check Supabase URL
if grep -q "EXPO_PUBLIC_SUPABASE_URL=https://ojcvjsxmshdvyxryunvk.supabase.co" .env; then
    echo "⚠️  Warning: Using default Supabase URL. Please update with your own."
fi

# Check Plaid credentials
if grep -q "PLAID_CLIENT_ID=68f9e88c17270900222dae83" .env; then
    echo "⚠️  Warning: Using default Plaid credentials. Please update with your own."
fi

echo "✅ Environment variables check completed"

# Start the development server
echo "🚀 Starting Expo development server..."
echo "   The app will be available at: http://localhost:8081"
echo "   Press 'a' to open Android emulator"
echo "   Press 'i' to open iOS simulator"
echo "   Press 'w' to open in web browser"
echo "   Press 'q' to quit"
echo ""

# Start Expo
expo start

echo "✅ Expo server stopped"