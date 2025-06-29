# Excel Shape Fixtures Setup

The following Excel files need manual shape creation since openpyxl cannot create shapes programmatically:

## obj_ok.xlsx
- Open in Excel
- Add a shape named "RefreshButton" to the Dashboard sheet
- Position it at approximately:
  - Top: 15 pt (20 pixels)
  - Left: 337.5 pt (450 pixels)
- Save the file

## obj_moved.xlsx  
- Open in Excel
- Add a shape named "RefreshButton" to the Dashboard sheet
- Position it at approximately:
  - Top: 15 pt (20 pixels)  
  - Left: 350 pt (466 pixels) - moved ~16 pixels right from expected
- Save the file

## Conversion Notes
- Excel uses points, tests expect pixels
- 1 point ≈ 1.333 pixels
- Expected position: top=20px, left=450px
- Moved position: top=20px, left=466px (16px difference > 5px tolerance)