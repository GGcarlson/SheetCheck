# SheetCheck Use Cases

This document outlines the various ways SheetCheck can be used across different industries, workflows, and scenarios. SheetCheck provides structural, data, and visual validation capabilities for Excel workbooks.

## Table of Contents

- [Financial Services & Audit](#financial-services--audit)
- [Regulatory Compliance](#regulatory-compliance)
- [Business Intelligence & Reporting](#business-intelligence--reporting)
- [Quality Assurance & Testing](#quality-assurance--testing)
- [Template Validation](#template-validation)
- [CI/CD Integration](#cicd-integration)
- [Data Migration & ETL](#data-migration--etl)
- [Academic & Research](#academic--research)
- [Corporate Finance](#corporate-finance)
- [Real Estate & Property Management](#real-estate--property-management)

---

## Financial Services & Audit

### 1. Financial Model Validation
**Problem**: Financial models contain complex formulas that can break during updates, leading to incorrect calculations in critical business decisions.

**SheetCheck Solution**:
```bash
# Validate quarterly financial model
validator Q4_Financial_Model.xlsx --rules rules/financial_model.yaml

# Compare models between quarters
validator Q3_Model.xlsx Q4_Model.xlsx --mode diff --report json,md
```

**Rule Example**:
```yaml
sheets:
  "Cash Flow":
    must_exist: true
    cells:
      D15:
        formula: "=SUM(D5:D14)"  # Total cash flow calculation
      E15:
        formula: "=D15+E5"       # Running balance
  "P&L":
    expect_cf_rules:
      - range: "C5:C20"
        type: "colorScale"
        colors: ["#FF0000", "#FFFF00", "#00FF00"]  # Red-yellow-green for variance
```

**Benefits**:
- Prevent broken formulas in financial calculations
- Ensure formatting consistency across reporting periods
- Validate that critical sheets and calculations exist
- Track visual changes in financial presentations

### 2. Audit Trail Validation
**Problem**: Auditors need to verify that Excel workbooks haven't been tampered with and follow required formatting standards.

**SheetCheck Solution**:
```bash
# Validate audit workbook against compliance rules
validator Audit_Workbook_2024.xlsx --rules rules/audit_standards.yaml

# Generate compliance report for auditors
validator Client_Financials.xlsx --report xml,md --rules rules/sox_compliance.yaml
```

**Benefits**:
- Automated compliance checking
- Consistent audit documentation
- Reduced manual review time
- Standardized reporting formats

---

## Regulatory Compliance

### 3. SOX Compliance Validation
**Problem**: Sarbanes-Oxley requires specific controls and formatting for financial reporting spreadsheets.

**SheetCheck Solution**:
```yaml
# SOX compliance rules
sheets:
  "Controls Matrix":
    must_exist: true
    cells:
      A1: 
        value: "SOX Controls Documentation"
  "Sign-offs":
    must_exist: true
    expect_cf_rules:
      - range: "E2:E50"
        type: "dataBar"  # Visual indicator of completion status

# Data validation for critical fields
rule_type: "data_validation"
target:
  sheet: "Controls Matrix"
expectations:
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "Control_ID"
  - expectation_type: "expect_column_values_to_be_in_set"
    kwargs:
      column: "Risk_Level"
      value_set: ["High", "Medium", "Low"]
```

### 4. Banking Regulatory Reports
**Problem**: Banks must submit standardized reports to regulators with exact formatting and data validation requirements.

**SheetCheck Solution**:
```bash
# Validate Basel III capital adequacy report
validator Basel_III_Report.xlsx --rules rules/basel_compliance.yaml

# Check CCAR stress test submission
validator CCAR_Submission.xlsx --rules rules/fed_requirements.yaml
```

---

## Business Intelligence & Reporting

### 5. Dashboard Template Validation
**Problem**: Business dashboards must maintain consistent formatting, colors, and data ranges across multiple teams and time periods.

**SheetCheck Solution**:
```bash
# Validate monthly dashboard template
validator Monthly_Dashboard.xlsx --rules rules/dashboard_standards.yaml

# Compare dashboard versions for consistency
validator Dashboard_v1.xlsx Dashboard_v2.xlsx --mode diff
```

**Rule Example**:
```yaml
sheets:
  "Executive Summary":
    expect_cf_rules:
      - range: "B5:B15"
        type: "colorScale"
        colors: ["#FF6B6B", "#FFE66D", "#4ECDC4"]  # Traffic light system
  "KPI Metrics":
    cells:
      C2:
        formula: "=AVERAGE(Data!C:C)"
      D2:
        formula: "=MAX(Data!D:D)"
    
# Data validation for KPI ranges
rule_type: "data_validation"
target:
  sheet: "KPI Metrics"
expectations:
  - expectation_type: "expect_column_values_to_be_between"
    kwargs:
      column: "Revenue"
      min_value: 0
      max_value: 100000000
```

### 6. Sales Performance Reports
**Problem**: Sales teams need consistent reporting formats to track performance across regions and time periods.

**SheetCheck Solution**:
```bash
# Validate regional sales reports
validator Sales_Report_Q4.xlsx --rules rules/sales_template.yaml

# Ensure data quality in sales pipeline
validator Pipeline_Data.xlsx --rules rules/crm_validation.yaml
```

---

## Quality Assurance & Testing

### 7. Software Testing Validation
**Problem**: Test result spreadsheets must follow specific formats and contain required data for certification processes.

**SheetCheck Solution**:
```bash
# Validate test results spreadsheet
validator Test_Results_Build_123.xlsx --rules rules/testing_standards.yaml

# Compare test results between builds
validator Build_122_Results.xlsx Build_123_Results.xlsx --mode diff
```

**Rule Example**:
```yaml
# Test results validation
rule_type: "data_validation"
target:
  sheet: "Test Results"
expectations:
  - expectation_type: "expect_column_values_to_be_in_set"
    kwargs:
      column: "Status"
      value_set: ["Pass", "Fail", "Skip", "Blocked"]
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "Test_ID"
  - expectation_type: "expect_column_values_to_match_regex"
    kwargs:
      column: "Build_Number"
      regex: "^\\d+\\.\\d+\\.\\d+$"  # Version format: x.y.z
```

### 8. Manufacturing Quality Control
**Problem**: Quality control spreadsheets must track measurements within tolerance ranges and flag out-of-spec conditions.

**SheetCheck Solution**:
```bash
# Validate production quality data
validator Quality_Control_Batch_456.xlsx --rules rules/qc_standards.yaml
```

---

## Template Validation

### 9. Corporate Template Standardization
**Problem**: Organizations need to ensure that Excel templates are used consistently across departments and maintain corporate branding.

**SheetCheck Solution**:
```bash
# Validate expense report template
validator Expense_Report_Template.xlsx --rules rules/corporate_template.yaml

# Check project planning template
validator Project_Plan_Template.xlsx --rules rules/pmo_standards.yaml
```

**Rule Example**:
```yaml
sheets:
  "Header":
    cells:
      A1:
        value: "Company Name Inc."
      A2:
        formula: "=TODAY()"  # Current date
    expect_cf_rules:
      - range: "A1:Z1"
        type: "fill"
        color: "#003366"  # Corporate blue header

  "Instructions":
    must_exist: true
    cells:
      A1:
        value: "Template Instructions"
```

### 10. Invoice Template Validation
**Problem**: Invoice templates must calculate totals correctly and maintain proper formatting for legal and accounting requirements.

**SheetCheck Solution**:
```bash
# Validate invoice template before distribution
validator Invoice_Template_2024.xlsx --rules rules/invoice_validation.yaml
```

---

## CI/CD Integration

### 11. Automated Spreadsheet Testing
**Problem**: Development teams need to automatically validate Excel files as part of their continuous integration pipeline.

**SheetCheck Solution**:
```yaml
# GitHub Actions workflow
name: Excel Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Install SheetCheck
      run: pip install sheetcheck
    - name: Validate Reports
      run: |
        validator reports/monthly_report.xlsx --rules rules/report_standards.yaml
        validator templates/*.xlsx --rules rules/template_validation.yaml
```

### 12. Release Validation
**Problem**: Before software releases, all documentation and reporting templates must be validated for correctness.

**SheetCheck Solution**:
```bash
# Pre-release validation script
#!/bin/bash
echo "Validating release documentation..."
validator docs/Release_Notes.xlsx --rules rules/documentation.yaml
validator reports/Performance_Metrics.xlsx --rules rules/metrics.yaml

if [ $? -eq 0 ]; then
    echo "✅ All Excel files validated successfully"
else
    echo "❌ Validation failed - blocking release"
    exit 1
fi
```

---

## Data Migration & ETL

### 13. Data Import Validation
**Problem**: When importing data from Excel files, you need to ensure the format and content meet requirements before processing.

**SheetCheck Solution**:
```bash
# Validate data import file
validator Customer_Data_Import.xlsx --rules rules/import_validation.yaml

# Check data quality before ETL process
validator Raw_Data.xlsx --rules rules/etl_requirements.yaml
```

**Rule Example**:
```yaml
# Data import validation
rule_type: "data_validation"
target:
  sheet: "Customer Data"
expectations:
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "Customer_ID"
  - expectation_type: "expect_column_values_to_match_regex"
    kwargs:
      column: "Email"
      regex: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
  - expectation_type: "expect_column_values_to_be_of_type"
    kwargs:
      column: "Registration_Date"
      type_: "datetime"
validation:
  success_threshold: 0.99  # 99% of records must be valid
```

### 14. Legacy System Migration
**Problem**: When migrating from legacy systems, Excel files serve as intermediate data stores that must be validated for completeness and accuracy.

**SheetCheck Solution**:
```bash
# Validate legacy data export
validator Legacy_Export_2024.xlsx --rules rules/migration_validation.yaml

# Compare pre and post migration data
validator Pre_Migration.xlsx Post_Migration.xlsx --mode diff
```

---

## Academic & Research

### 15. Research Data Validation
**Problem**: Academic researchers need to ensure their data collection spreadsheets follow proper formats and contain valid data ranges.

**SheetCheck Solution**:
```bash
# Validate research dataset
validator Survey_Results_Study_123.xlsx --rules rules/research_standards.yaml

# Check experimental data
validator Lab_Results_Experiment_A.xlsx --rules rules/lab_validation.yaml
```

**Rule Example**:
```yaml
# Research data validation
rule_type: "data_validation"
target:
  sheet: "Survey Data"
expectations:
  - expectation_type: "expect_column_values_to_be_between"
    kwargs:
      column: "Age"
      min_value: 18
      max_value: 100
  - expectation_type: "expect_column_values_to_be_in_set"
    kwargs:
      column: "Gender"
      value_set: ["Male", "Female", "Other", "Prefer not to say"]
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "Participant_ID"
```

### 16. Grant Reporting Validation
**Problem**: Grant applications and reports must follow specific formatting requirements from funding agencies.

**SheetCheck Solution**:
```bash
# Validate NSF grant budget
validator NSF_Budget_Proposal.xlsx --rules rules/nsf_requirements.yaml

# Check NIH progress report
validator NIH_Progress_Report.xlsx --rules rules/nih_standards.yaml
```

---

## Corporate Finance

### 17. Budget Planning Validation
**Problem**: Annual budget spreadsheets must maintain consistency across departments and follow corporate standards.

**SheetCheck Solution**:
```bash
# Validate departmental budgets
validator IT_Budget_2025.xlsx --rules rules/budget_template.yaml
validator Marketing_Budget_2025.xlsx --rules rules/budget_template.yaml

# Compare budget versions
validator Budget_Draft_v1.xlsx Budget_Final_v2.xlsx --mode diff
```

### 18. Expense Reporting
**Problem**: Employee expense reports must follow company policies and calculation rules.

**SheetCheck Solution**:
```bash
# Validate expense report
validator Employee_Expenses_Q4.xlsx --rules rules/expense_policy.yaml
```

**Rule Example**:
```yaml
sheets:
  "Expenses":
    cells:
      F2:
        formula: "=SUM(D2:E2)"  # Total = Meals + Travel
      G2:
        formula: "=F2*0.1"      # Tax calculation
    
rule_type: "data_validation"
target:
  sheet: "Expenses"
expectations:
  - expectation_type: "expect_column_values_to_be_between"
    kwargs:
      column: "Meal_Amount"
      min_value: 0
      max_value: 75  # Company meal limit
  - expectation_type: "expect_column_values_to_be_between"
    kwargs:
      column: "Travel_Amount"
      min_value: 0
      max_value: 2000  # Company travel limit
```

---

## Real Estate & Property Management

### 19. Property Valuation Reports
**Problem**: Real estate valuations must follow industry standards and contain required calculations and formatting.

**SheetCheck Solution**:
```bash
# Validate property appraisal
validator Property_Valuation_123_Main_St.xlsx --rules rules/appraisal_standards.yaml

# Compare market analysis reports
validator Market_Analysis_Q3.xlsx Market_Analysis_Q4.xlsx --mode diff
```

### 20. Rent Roll Validation
**Problem**: Property management companies need to ensure rent roll spreadsheets calculate totals correctly and flag delinquent accounts.

**SheetCheck Solution**:
```bash
# Validate monthly rent roll
validator Rent_Roll_December_2024.xlsx --rules rules/rent_roll_validation.yaml
```

**Rule Example**:
```yaml
sheets:
  "Rent Roll":
    cells:
      H1:
        formula: "=SUM(H2:H100)"  # Total rent collected
    expect_cf_rules:
      - range: "G2:G100"
        type: "dataBar"
        color: "#FF0000"  # Red bars for delinquent accounts

rule_type: "data_validation"
target:
  sheet: "Rent Roll"
expectations:
  - expectation_type: "expect_column_values_to_be_between"
    kwargs:
      column: "Monthly_Rent"
      min_value: 500
      max_value: 5000
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "Unit_Number"
```

---

## Implementation Examples

### Basic Validation Command
```bash
# Simple validation with default rules
validator my_workbook.xlsx

# Custom rules with specific output
validator my_workbook.xlsx --rules custom_rules.yaml --report json,md,xml
```

### Advanced CI/CD Integration
```yaml
# .github/workflows/excel-validation.yml
name: Excel File Validation
on: [push, pull_request]

jobs:
  validate-excel:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install SheetCheck
      run: pip install sheetcheck
    - name: Validate Excel Files
      run: |
        find . -name "*.xlsx" -exec validator {} --rules rules/corporate_standards.yaml \;
```

### Custom Rule Development
```yaml
# rules/my_custom_rules.yaml
sheets:
  "Data Entry":
    must_exist: true
    cells:
      A1:
        value: "Data Entry Form v2.0"
      B1:
        formula: "=TODAY()"
    expect_cf_rules:
      - range: "A1:Z1"
        type: "fill"
        color: "#0066CC"

rule_type: "data_validation"
target:
  sheet: "Data Entry"
expectations:
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "ID"
  - expectation_type: "expect_column_values_to_be_unique"
    kwargs:
      column: "ID"
validation:
  success_threshold: 1.0  # 100% compliance required
```

---

## Getting Started

1. **Install SheetCheck**: `pip install sheetcheck`
2. **Choose your use case** from the examples above
3. **Create custom rules** based on your requirements
4. **Integrate into your workflow** (manual, CI/CD, or automated)
5. **Monitor and iterate** on your validation rules

For more details, see:
- [README.md](README.md) - Installation and basic usage
- [CLAUDE.md](CLAUDE.md) - Development guidance
- [PRD.md](PRD.md) - Product requirements and architecture

SheetCheck provides the flexibility to handle any Excel validation scenario while maintaining consistency, accuracy, and compliance across your organization.