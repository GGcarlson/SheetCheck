# Excel-Validator – PRD

## Problem
Auditors (starting with me!) waste hours eyeballing newly-generated Excel workbooks:
* Broken or hard-coded formulas
* Missing conditional-formatting rules
* Mis-placed buttons/objects after macro runs
* Visual drift between "last year" and "this year"

## Goal
Ship a CLI tool that:
1. **Loads** `.xlsx/.xlsm` (+ CSV) workbooks
2. **Applies** declarative rules for structure, data and visuals
3. **Outputs** JSON + JUnit + human-readable summaries
4. **Fails CI** when any rule breaks
5. Feeds structured failures back to Claude Code so it can auto-repair workbooks

## Success metrics
| Metric | Target for v1 |
|--------|---------------|
| Structural rule coverage | Sheets, cell formulas, conditional formatting, objects |
| Mean validation run-time (50 MB workbook) | ≤ 15 s local |
| CI adoption (my repos) | 100 % by FY-25 audits |
| Bug reports during audit season | < 2 per template |

## Scope
### In-scope MVP
- XLSX/XLSM ingest (openpyxl + xlwings)
- YAML rule files + Python hooks
- Sheet/Cell/CF/Object rules
- Baseline PNG capture (COM on Windows, HTML+Puppeteer fallback)
- Pixel-diff with configurable threshold
- JSON + JUnit + Markdown reporters
- GitHub Actions workflow

### Out-of-scope (v2+)
- XLSB support  
- PDF extraction  
- OCR semantic visual diffs  
- Auto-patching workbooks (will be handled by Claude Code, not the validator)

## Stakeholders
| Role | Name |
|------|------|
| Product owner | **You** |
| Lead engineer | Claude Code (+ you for review) |
| Audit SMEs     | Future teammates |

## High-level architecture
```text
CLI ──► Rule Engine ──► Structural checks
     │                └► Data checks (pandas + GE)
     │                └► Visual checks
     │                        ▲
     │                        │ screenshot provider (COM | HTML)
     └──► Reporter (JSON, JUnit, MD)
```