#!/bin/bash

# SheetCheck - Start Puppeteer MCP Server
# This script starts the Puppeteer MCP server for local development

echo "🚀 Starting Puppeteer MCP Server..."
echo "Server will be available at: http://localhost:8085"
echo "Press Ctrl+C to stop the server"
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found. Please install Node.js"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if Docker is available (alternative method)
if command -v docker &> /dev/null; then
    echo "🐳 Docker available - you can also run:"
    echo "   docker run -p 8085:80 --rm mcp/puppeteer:latest"
    echo ""
fi

# Start the MCP server using npx
echo "📦 Starting with npx @modelcontextprotocol/server-puppeteer..."
npx @modelcontextprotocol/server-puppeteer

# If npx fails, show Docker alternative
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ npx failed. Try Docker alternative:"
    echo "   docker run -p 8085:80 --rm mcp/puppeteer:latest"
    echo ""
    echo "Or install the package globally:"
    echo "   npm install -g @modelcontextprotocol/server-puppeteer"
fi