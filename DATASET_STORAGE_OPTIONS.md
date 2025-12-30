# Fish Health Dataset - Storage Options

## Problem
The fish health dataset (131 MB, 4,428 images) is too large to push directly to GitHub. GitHub has limitations on:
- Single file size: 100 MB max
- Push size: Timeouts occur with large pushes (>100 MB)
- Repository size: Best practice is to keep repos under 1 GB

## ✅ Recommended Solutions

### Option 1: Git LFS (Git Large File Storage) - BEST FOR GITHUB

**Install Git LFS:**
```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install git-lfs

# Initialize in your repo
cd /home/koi/Documents/GitHub/ishara-iot
git lfs install

# Track the dataset images
git lfs track "dataset/fish_health/**/*.jpg"
git lfs track "dataset/fish_health/**/*.png"

# Add .gitattributes
git add .gitattributes

# Now add and commit the dataset
git add dataset/fish_health/
git commit -m "Add fish health dataset using Git LFS"
git push origin main
```

**Advantages:**
- ✅ Dataset stays in the same repo
- ✅ GitHub supports Git LFS for free (1 GB storage, 1 GB bandwidth/month)
- ✅ Easy for others to clone
- ✅ Version control for dataset

### Option 2: Cloud Storage + Download Script - EASIEST

**Upload to cloud storage:**
1. Google Drive
2. Dropbox
3. OneDrive
4. Mega.nz

**Then create a download script:**
```bash
#!/bin/bash
# download_dataset.sh

echo "Downloading fish health dataset..."
echo "Please download from: [YOUR_LINK_HERE]"
echo "Extract to: dataset/fish_health/"
echo ""
echo "Or use gdown (for Google Drive):"
echo "pip install gdown"
echo "gdown [GOOGLE_DRIVE_FILE_ID]"
echo "unzip dataset.zip -d dataset/"
```

### Option 3: Release Assets - GOOD FOR GITHUB

**Use GitHub Releases:**
1. Create a ZIP of the dataset locally
2. Go to GitHub repo → Releases → Create new release
3. Upload the ZIP as a release asset (up to 2 GB per file)

```bash
# Create compressed archive
cd /home/koi/Documents/GitHub/ishara-iot
tar -czf fish_health_dataset.tar.gz dataset/fish_health/

# Or create a zip
zip -r fish_health_dataset.zip dataset/fish_health/
```

Then:
- Go to: https://github.com/Ishara-Sewwandi/ishara-iot/releases
- Click "Create a new release"
- Upload `fish_health_dataset.tar.gz`
- Users can download from releases

### Option 4: Dataset Hosting Services - BEST FOR SHARING

**Specialized dataset hosting:**

1. **Kaggle Datasets** (free, unlimited)
   - Upload to: https://www.kaggle.com/datasets
   - Public datasets get DOI
   - Easy integration

2. **Roboflow** (free for public datasets)
   - Computer vision focused
   - Automatic format conversion
   - API access

3. **Hugging Face Datasets** (free)
   - ML-focused
   - Version control
   - Easy downloads

4. **Zenodo** (free, academic)
   - Gets DOI citation
   - Good for research

## 🚀 Quick Start: Let's Use Git LFS

I recommend Git LFS. Here's the complete setup:

```bash
# Step 1: Install Git LFS
sudo apt-get install git-lfs

# Step 2: Initialize
cd /home/koi/Documents/GitHub/ishara-iot
git lfs install

# Step 3: Track image files
git lfs track "dataset/fish_health/**/*.jpg"
git lfs track "dataset/fish_health/**/*.png"

# Step 4: Commit the tracking file
git add .gitattributes
git commit -m "Setup Git LFS for dataset"

# Step 5: Add dataset
git add dataset/fish_health/
git commit -m "Add fish health dataset (4,428 images)"

# Step 6: Push (Git LFS will handle the large files)
git push origin main
```

## 📝 Current Status

The dataset is ready locally but not pushed to GitHub due to size limitations.

**Dataset Info:**
- Location: `dataset/fish_health/`
- Size: 131 MB
- Files: 4,428 images
- Classes: 6 (healthy, bacterial, fungal, parasitic, dead, white_tail)

## 💡 My Recommendation

Use **Git LFS** if you want it in the repo, or use **GitHub Releases** for simplicity.

For now, the dataset remains local only. Users can create their own datasets following the instructions in `dataset/DATASET_README.md`.

---

**Need help?** Choose one of the options above and I can help you set it up!
