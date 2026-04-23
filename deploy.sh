#!/bin/bash
set -e

cd /root/rmi/rmi-frontend

echo "Cleaning up..."
rm -rf node_modules package-lock.json

echo "Installing dependencies..."
npm install --legacy-peer-deps

echo "Building..."
npm run build

echo "Deploying to Vercel..."
vercel --prod --yes

echo "Done!"
