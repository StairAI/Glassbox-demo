#!/bin/bash
# Clear all test data

echo "=================================================="
echo "CLEARING OLD TEST DATA"
echo "=================================================="
echo

# 1. Clear trigger registry (SUI simulation)
echo "1. Clearing trigger registry..."
if [ -f "data/trigger_registry.json" ]; then
    rm data/trigger_registry.json
    echo "   ✓ Removed trigger_registry.json"
else
    echo "   ℹ trigger_registry.json not found"
fi

# 2. Clear activity database
echo
echo "2. Clearing activity database..."
if [ -f "data/activity.db" ]; then
    rm data/activity.db
    echo "   ✓ Removed activity.db"
else
    echo "   ℹ activity.db not found"
fi

# 3. Note about Walrus (can't delete from real testnet)
echo
echo "3. Walrus data:"
echo "   ℹ Data on Walrus testnet CANNOT be deleted"
echo "   ℹ Old blobs will remain but won't be referenced"
echo "   ℹ New triggers will use new blob_ids"

echo
echo "=================================================="
echo "DATA CLEARED"
echo "=================================================="
echo
echo "Next steps:"
echo "  1. Run your new batch processing script"
echo "  2. Refresh the visualization (http://localhost:8080)"
echo "  3. Only new data will appear"
echo
