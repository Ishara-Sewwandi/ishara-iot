# Fish Health Dataset

## Structure

```
fish_health/
├── train/          # Training images
│   ├── healthy/
│   ├── bacterial/
│   ├── fungal/
│   ├── parasitic/
│   ├── dead/
│   └── white_tail/
├── val/            # Validation images
│   ├── healthy/
│   ├── bacterial/
│   ├── fungal/
│   ├── parasitic/
│   ├── dead/
│   └── white_tail/
└── test/           # Test images
    ├── healthy/
    ├── bacterial/
    ├── fungal/
    ├── parasitic/
    ├── dead/
    └── white_tail/
```

## Adding Images

1. Place your fish images in the appropriate category folders
2. Images will be committed in batches of 20 for GitHub compatibility
3. Supported formats: JPG, PNG

## Classes

- **healthy**: Healthy fish
- **bacterial**: Bacterial infections
- **fungal**: Fungal infections  
- **parasitic**: Parasitic infections
- **dead**: Dead fish
- **white_tail**: White tail disease
