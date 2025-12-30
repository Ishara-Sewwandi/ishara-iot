#!/bin/bash
# Monitor fish health classifier training progress

cd /home/koi/Documents/GitHub/ishara-iot

echo "=========================================="
echo "Fish Health Training Monitor"
echo "=========================================="
echo ""

# Check if training is running
if ps aux | grep "train_fish_health_classifier.py" | grep -v grep > /dev/null; then
    echo "✅ Training is RUNNING"
    echo ""
    
    # Show last 30 lines of log
    echo "📊 Latest Progress:"
    echo "------------------------------------------"
    tail -30 training.log | grep -E "(Epoch|epoch|loss|top1|top5|✅|Complete|Error)" || tail -30 training.log
    
    echo ""
    echo "------------------------------------------"
    echo "📁 Training output: runs/classify/fish_health/"
    echo "📝 Full log: training.log"
    echo ""
    echo "Commands:"
    echo "  tail -f training.log          # Watch live progress"
    echo "  ./monitor_training.sh         # Check status again"
    echo "  pkill -f train_fish_health    # Stop training"
else
    echo "⚠️  Training is NOT running"
    echo ""
    echo "Check if it completed:"
    if [ -f "models/fish_health_classifier.pt" ]; then
        echo "✅ Model found: models/fish_health_classifier.pt"
        ls -lh models/fish_health_classifier.pt
    else
        echo "❌ Model not found yet"
    fi
    
    echo ""
    echo "Last 50 lines of log:"
    echo "------------------------------------------"
    tail -50 training.log
fi
