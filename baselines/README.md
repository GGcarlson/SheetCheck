# Baseline Images Directory

This directory contains baseline PNG images for visual comparison testing.

## Directory Structure

```
baselines/
├── README.md          # This file
├── sheets/           # Baseline images for sheet captures
│   ├── workbook1/
│   │   ├── Sheet1.png
│   │   └── Dashboard.png
│   └── workbook2/
│       └── Summary.png
└── components/       # Baseline images for UI components
    ├── charts/
    └── tables/
```

## Usage

1. **Capturing Baselines**: Use the visual capture functionality to create baseline images:
   ```python
   from src.visual.capture_com import capture_sheet_png
   capture_sheet_png("workbook.xlsx", "Sheet1", "baselines/sheets/workbook1/Sheet1.png")
   ```

2. **Comparing Against Baselines**: Use the pixel diff functionality:
   ```python
   from src.visual.pixel_diff import diff_png
   diff_ratio = diff_png(
       "baselines/sheets/workbook1/Sheet1.png", 
       "actual_capture.png",
       threshold=0.02
   )
   ```

## Best Practices

- **Naming Convention**: Use descriptive names that match your workbook and sheet names
- **Organization**: Group related baselines in subdirectories
- **Version Control**: Commit baseline images to ensure consistency across environments
- **Updates**: Review and update baselines when legitimate visual changes occur
- **Thresholds**: Use appropriate threshold values (default 0.02 = 2% difference tolerance)

## File Formats

- All baseline images should be PNG format for lossless compression
- Images should be captured at consistent resolution and DPI settings
- Ensure proper color depth (RGBA recommended for transparency support)