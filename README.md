# Python Code Checker

A lightweight tool for analyzing Python code quality and detecting common issues

---

## What does it do?

This tool scans your Python files and gives you:
- Quality score out of 100
- List of issues found
- Detailed statistics about your code
- Beautiful reports in terminal, JSON, or HTML

---

## Features

- Function length analysis
- Code complexity measurement
- Documentation checker
- Security warnings for dangerous functions
- PEP 8 line length validation
- Multiple export formats
- Colored terminal output

---

## Quick Start

Install:
```bash
pip install colorama
```

Run:
```bash
python checker.py yourfile.py
```

---

## Usage Examples

Check single file:
```bash
python checker.py script.py
```

Check entire project:
```bash
python checker.py /path/to/project
```

Export as JSON:
```bash
python checker.py script.py --json
```

Export as HTML:
```bash
python checker.py script.py --html
```

---

## Sample Output
```
============================================================
تقرير فحص الكود: example.py
============================================================

الإحصائيات:
  - إجمالي الأسطر: 45
  - عدد الدوال: 3
  - متوسط التعقيد: 4.3

المشاكل المكتشفة:
  [تحذير] السطر 10: الدالة طويلة جداً
  [ملاحظة] السطر 5: بدون توثيق

درجة جودة الكود: 93/100
تقييم: ممتاز ✓
```

---

## What gets checked?

**Errors** - Critical issues that need immediate attention:
- Using eval() or exec() functions

**Warnings** - Important issues to fix:
- Functions longer than 50 lines
- Code complexity higher than 10
- Functions with more than 5 parameters
- Empty classes without methods

**Notes** - Minor improvements:
- Missing docstrings
- Lines longer than 79 characters

---

## Scoring System

Starting from 100 points:
- Each error: -10 points
- Each warning: -5 points
- Each note: -2 points

Rating:
- 90-100: Excellent
- 70-89: Good
- 50-69: Acceptable
- Below 50: Needs work

---

## Export Formats

### JSON
Perfect for automation and CI/CD pipelines
```bash
python checker.py code.py --json
```

### HTML
Visual report you can open in browser
```bash
python checker.py code.py --html
```

---

## Requirements

- Python 3.6+
- colorama (optional, for colors)

---

## License

MIT License - feel free to use and modify

---

**Made by Rlk-code**
