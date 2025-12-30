#!/bin/bash

# Batch Upload Dataset to GitHub
# This script copies images in batches of 20 and pushes to GitHub

BATCH_SIZE=20
REPO_DIR="/home/koi/Documents/GitHub/ishara-iot"
DATASET_DIR="$REPO_DIR/dataset/fish_health"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd "$REPO_DIR"

echo -e "${BLUE}=== Batch Dataset Upload Script ===${NC}"
echo ""

# Function to process images in batches
process_category() {
    local category=$1
    local split=$2  # train/val/test
    local source_dir=$3
    
    echo -e "${GREEN}Processing ${category} - ${split}...${NC}"
    
    if [ ! -d "$source_dir" ]; then
        echo -e "${RED}Source directory not found: $source_dir${NC}"
        return
    fi
    
    # Count total images
    total_images=$(find "$source_dir" -maxdepth 1 \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | wc -l)
    
    if [ $total_images -eq 0 ]; then
        echo "No images found in $source_dir"
        return
    fi
    
    echo "Found $total_images images"
    
    # Calculate number of batches
    batches=$(( ($total_images + $BATCH_SIZE - 1) / $BATCH_SIZE ))
    
    batch_num=1
    
    # Process images in batches
    find "$source_dir" -maxdepth 1 \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" \) | while read -r line; do
        images+=("$line")
        
        if [ ${#images[@]} -eq $BATCH_SIZE ] || [ $batch_num -eq $batches ]; then
            echo -e "${BLUE}Batch $batch_num of $batches (${#images[@]} images)${NC}"
            
            # Copy images to dataset folder
            dest_dir="$DATASET_DIR/$split/$category"
            mkdir -p "$dest_dir"
            
            for img in "${images[@]}"; do
                cp "$img" "$dest_dir/"
            done
            
            # Git add and commit
            git add "$dest_dir"
            git commit -m "Batch $batch_num: Add ${#images[@]} $category images ($split set)"
            
            # Push to GitHub
            echo "Pushing batch $batch_num to GitHub..."
            git push origin main
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ Batch $batch_num uploaded successfully${NC}"
            else
                echo -e "${RED}✗ Failed to push batch $batch_num${NC}"
                exit 1
            fi
            
            # Clear array for next batch
            images=()
            ((batch_num++))
            
            # Small delay to avoid overwhelming GitHub
            sleep 2
        fi
    done
}

# Check if source directory argument provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <source_dataset_directory>"
    echo ""
    echo "Example: $0 /path/to/your/fish_images"
    echo ""
    echo "Expected structure:"
    echo "  source_directory/"
    echo "    ├── train/"
    echo "    │   ├── healthy/"
    echo "    │   ├── bacterial/"
    echo "    │   ├── fungal/"
    echo "    │   ├── parasitic/"
    echo "    │   ├── dead/"
    echo "    │   └── white_tail/"
    echo "    ├── val/"
    echo "    │   └── (same categories)"
    echo "    └── test/"
    echo "        └── (same categories)"
    exit 1
fi

SOURCE_DIR=$1

if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Source directory not found: $SOURCE_DIR${NC}"
    exit 1
fi

echo "Source: $SOURCE_DIR"
echo "Destination: $DATASET_DIR"
echo "Batch size: $BATCH_SIZE images"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Process each category and split
categories=("healthy" "bacterial" "fungal" "parasitic" "dead" "white_tail")
splits=("train" "val" "test")

for split in "${splits[@]}"; do
    for category in "${categories[@]}"; do
        source_path="$SOURCE_DIR/$split/$category"
        if [ -d "$source_path" ]; then
            process_category "$category" "$split" "$source_path"
        fi
    done
done

echo ""
echo -e "${GREEN}=== Upload Complete! ===${NC}"
