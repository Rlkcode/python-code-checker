python-code-checker

A simple Python tool to check and analyze code quality and detect problems and issues

---

## Features

- Check function length
- Measure code complexity
- Verify documentation exists
- Detect dangerous usage like eval and exec
- Check line length
- Export reports as JSON and HTML
- Colorful terminal interface

---

## Installation

Requires Python 3.6 or higher

`bash
pip install coloramaUsageCheck a file:python checker.py myfile.pyCheck a folder:python checker.py myproject/Save JSON report:python checker.py myfile.py --jsonSave HTML report:python checker.py myfile.py --htmlExample Output
============================================================
تقرير فحص الكود: example.py
============================================================

الإحصائيات:
  - إجمالي الأسطر: 45
  - عدد الدوال: 3
  - عدد الكلاسات: 1

المشاكل المكتشفة:

  [تحذير] السطر 10: الدالة طويلة جداً
  [ملاحظة] السطر 5: الدالة بدون توثيق



📝 الرخصة

هذا المشروع مرخص تحت MIT License

👤 المطورRlk-code
GitHub: @
⭐ دعم المشروع

إذا أعجبتك الأداة، لا تنسَ إعطاء المشروع نجمة ⭐
صُنع بـ 💙 بواسطة Rlk-code
  
