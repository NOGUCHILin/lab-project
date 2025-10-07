#!/usr/bin/env bash
# NixOS Deployment with Testing

set -e

echo "🧪 Running E2E Tests..."
npm run test

if [ $? -eq 0 ]; then
    echo "✅ All tests passed! Proceeding with deployment..."
    
    echo "🚀 Rebuilding NixOS system..."
    sudo nixos-rebuild switch --flake /home/noguchilin/nixos-config#nixos
    
    echo "✅ Deployment completed successfully!"
    
    # Post-deployment health check
    echo "🏥 Running post-deployment health check..."
    sleep 10  # Wait for services to start
    
    # Check if dashboard is responding
    if curl -sf https://nixos.tail4ed625.ts.net/ > /dev/null; then
        echo "✅ Dashboard is responding"
    else
        echo "❌ Dashboard health check failed"
        exit 1
    fi
    
else
    echo "❌ Tests failed! Deployment aborted."
    exit 1
fi