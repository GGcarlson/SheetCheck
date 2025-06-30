#!/usr/bin/env node

/**
 * SheetCheck - Excel to HTML Renderer
 * 
 * Converts Excel sheets to HTML using SheetJS library for cross-platform
 * visual validation via Puppeteer MCP screenshot capture.
 * 
 * Usage: node render_html.js input.xlsx [SheetName] > output.html
 * 
 * Requirements: npm install xlsx
 */

const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

function main() {
    // Parse command line arguments
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.error('Usage: node render_html.js input.xlsx [SheetName] > output.html');
        console.error('');
        console.error('Examples:');
        console.error('  node render_html.js data.xlsx Dashboard > dashboard.html');
        console.error('  node render_html.js data.xlsx > first_sheet.html');
        process.exit(1);
    }

    const excelPath = args[0];
    const sheetName = args[1]; // Optional - uses first sheet if not specified

    // Validate input file exists
    if (!fs.existsSync(excelPath)) {
        console.error(`Error: File not found: ${excelPath}`);
        process.exit(1);
    }

    try {
        // Read Excel workbook
        const workbook = XLSX.readFile(excelPath);
        
        // Get target sheet
        let targetSheet;
        let targetSheetName;
        
        if (sheetName) {
            // Use specified sheet name
            if (!(sheetName in workbook.Sheets)) {
                console.error(`Error: Sheet '${sheetName}' not found in workbook`);
                console.error(`Available sheets: ${Object.keys(workbook.Sheets).join(', ')}`);
                process.exit(1);
            }
            targetSheet = workbook.Sheets[sheetName];
            targetSheetName = sheetName;
        } else {
            // Use first sheet
            targetSheetName = workbook.SheetNames[0];
            targetSheet = workbook.Sheets[targetSheetName];
        }

        // Convert sheet to HTML
        const htmlOutput = XLSX.utils.sheet_to_html(targetSheet, {
            id: 'excel-sheet',
            editable: false
        });

        // Create complete HTML document with styling
        const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Sheet: ${targetSheetName}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: white;
        }
        
        #excel-sheet {
            border-collapse: collapse;
            width: 100%;
            max-width: none;
        }
        
        #excel-sheet td, #excel-sheet th {
            border: 1px solid #d0d0d0;
            padding: 4px 8px;
            text-align: left;
            vertical-align: top;
            font-size: 12px;
            white-space: nowrap;
        }
        
        #excel-sheet th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        
        /* Handle empty cells */
        #excel-sheet td:empty::before {
            content: "\\00a0"; /* Non-breaking space */
        }
        
        /* Excel-like styling */
        #excel-sheet tr:nth-child(even) {
            background-color: #fafafa;
        }
        
        .sheet-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="sheet-title">Sheet: ${targetSheetName}</div>
    ${htmlOutput}
</body>
</html>`;

        // Output to stdout
        console.log(fullHtml);

    } catch (error) {
        console.error(`Error processing Excel file: ${error.message}`);
        process.exit(1);
    }
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error(`Uncaught exception: ${error.message}`);
    process.exit(1);
});

// Run main function
if (require.main === module) {
    main();
}