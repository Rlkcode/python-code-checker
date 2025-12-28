#!/usr/bin/env python3
import ast
import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    COLORS_ENABLED = False

def color_text(text, color_code):
    if COLORS_ENABLED:
        return color_code + text + Style.RESET_ALL
    return text

class CodeChecker:
    def __init__(self, filepath):
        self.filepath = filepath
        self.issues = []
        self.stats = {
            'functions': 0,
            'classes': 0,
            'lines': 0,
            'complexity': 0
        }
    
    def read_file(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(color_text(f"خطأ: الملف {self.filepath} غير موجود", Fore.RED))
            sys.exit(1)
        except Exception as e:
            print(color_text(f"خطأ في قراءة الملف: {e}", Fore.RED))
            sys.exit(1)
    
    def count_lines(self, content):
        lines = content.split('\n')
        self.stats['lines'] = len(lines)
        empty = sum(1 for line in lines if not line.strip())
        comments = sum(1 for line in lines if line.strip().startswith('#'))
        return len(lines), empty, comments
    
    def calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def check_function(self, node):
        self.stats['functions'] += 1
        func_name = node.name
        length = node.end_lineno - node.lineno
        complexity = self.calculate_complexity(node)
        
        self.stats['complexity'] += complexity
        
        if length > 50:
            self.issues.append({
                'type': 'warning',
                'line': node.lineno,
                'msg': f"الدالة '{func_name}' طويلة جداً ({length} سطر)"
            })
        
        if complexity > 10:
            self.issues.append({
                'type': 'warning',
                'line': node.lineno,
                'msg': f"الدالة '{func_name}' معقدة جداً (تعقيد: {complexity})"
            })
        
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append({
                'type': 'info',
                'line': node.lineno,
                'msg': f"الدالة '{func_name}' بدون توثيق"
            })
        
        args_count = len(node.args.args)
        if args_count > 5:
            self.issues.append({
                'type': 'warning',
                'line': node.lineno,
                'msg': f"الدالة '{func_name}' لديها {args_count} معاملات (كثيرة)"
            })
    
    def check_class(self, node):
        self.stats['classes'] += 1
        class_name = node.name
        
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append({
                'type': 'info',
                'line': node.lineno,
                'msg': f"الكلاس '{class_name}' بدون توثيق"
            })
        
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        if len(methods) == 0:
            self.issues.append({
                'type': 'warning',
                'line': node.lineno,
                'msg': f"الكلاس '{class_name}' فارغ (بدون methods)"
            })
    
    def check_dangerous_calls(self, node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    self.issues.append({
                        'type': 'error',
                        'line': node.lineno,
                        'msg': f"استخدام {node.func.id}() خطير أمنياً"
                    })
    
    def check_line_length(self, content):
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                self.issues.append({
                    'type': 'info',
                    'line': i,
                    'msg': f"السطر طويل ({len(line)} حرف) - يفضل أقل من 80"
                })
    
    def analyze(self):
        content = self.read_file()
        total_lines, empty_lines, comment_lines = self.count_lines(content)
        
        self.check_line_length(content)
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(color_text(f"خطأ في صياغة الكود: {e}", Fore.RED))
            sys.exit(1)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.check_function(node)
            elif isinstance(node, ast.ClassDef):
                self.check_class(node)
            
            self.check_dangerous_calls(node)
        
        return total_lines, empty_lines, comment_lines
    
    def print_report(self, total_lines, empty_lines, comment_lines):
        print(color_text("=" * 60, Fore.CYAN))
        print(color_text(f"تقرير فحص الكود: {os.path.basename(self.filepath)}", Fore.CYAN))
        print(color_text("=" * 60, Fore.CYAN))
        print()
        
        print(color_text("الإحصائيات:", Fore.YELLOW))
        print(f"  - إجمالي الأسطر: {total_lines}")
        print(f"  - أسطر فارغة: {empty_lines}")
        print(f"  - أسطر التعليقات: {comment_lines}")
        print(f"  - عدد الدوال: {self.stats['functions']}")
        print(f"  - عدد الكلاسات: {self.stats['classes']}")
        if self.stats['functions'] > 0:
            avg_complexity = self.stats['complexity'] / self.stats['functions']
            print(f"  - متوسط التعقيد: {avg_complexity:.1f}")
        print()
        
        if self.issues:
            print(color_text("المشاكل المكتشفة:", Fore.YELLOW))
            print()
            
            errors = [i for i in self.issues if i['type'] == 'error']
            warnings = [i for i in self.issues if i['type'] == 'warning']
            infos = [i for i in self.issues if i['type'] == 'info']
            
            for issue in errors:
                print(color_text(f"  [خطأ] السطر {issue['line']}: {issue['msg']}", Fore.RED))
            
            for issue in warnings:
                print(color_text(f"  [تحذير] السطر {issue['line']}: {issue['msg']}", Fore.YELLOW))
            
            for issue in infos[:10]:
                print(color_text(f"  [ملاحظة] السطر {issue['line']}: {issue['msg']}", Fore.BLUE))
            
            if len(infos) > 10:
                print(color_text(f"  ... و {len(infos) - 10} ملاحظة أخرى", Fore.BLUE))
            
            print()
            print(f"المجموع: {color_text(str(len(errors)), Fore.RED)} أخطاء, "
                  f"{color_text(str(len(warnings)), Fore.YELLOW)} تحذيرات, "
                  f"{color_text(str(len(infos)), Fore.BLUE)} ملاحظات")
        else:
            print(color_text("✓ لم يتم اكتشاف أي مشاكل!", Fore.GREEN))
        
        print(color_text("=" * 60, Fore.CYAN))
        
        score = 100
        score -= len([i for i in self.issues if i['type'] == 'error']) * 10
        score -= len([i for i in self.issues if i['type'] == 'warning']) * 5
        score -= len([i for i in self.issues if i['type'] == 'info']) * 2
        score = max(0, score)
        
        print(f"\nدرجة جودة الكود: {color_text(f'{score}/100', Fore.CYAN)}")
        
        if score >= 90:
            print(color_text("تقييم: ممتاز ✓", Fore.GREEN))
        elif score >= 70:
            print(color_text("تقييم: جيد", Fore.YELLOW))
        elif score >= 50:
            print(color_text("تقييم: مقبول", Fore.YELLOW))
        else:
            print(color_text("تقييم: يحتاج تحسين", Fore.RED))
    
    def export_json(self, output_file):
        report = {
            'file': self.filepath,
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'issues': self.issues,
            'score': max(0, 100 - len([i for i in self.issues if i['type'] == 'error']) * 10 
                        - len([i for i in self.issues if i['type'] == 'warning']) * 5 
                        - len([i for i in self.issues if i['type'] == 'info']) * 2)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(color_text(f"\n✓ تم حفظ التقرير في: {output_file}", Fore.GREEN))
    
    def export_html(self, output_file):
        errors = [i for i in self.issues if i['type'] == 'error']
        warnings = [i for i in self.issues if i['type'] == 'warning']
        infos = [i for i in self.issues if i['type'] == 'info']
        
        score = max(0, 100 - len(errors) * 10 - len(warnings) * 5 - len(infos) * 2)
        
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تقرير فحص الكود - {os.path.basename(self.filepath)}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-item {{ background: white; padding: 10px; border-radius: 5px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .issue {{ padding: 10px; margin: 5px 0; border-right: 4px solid; border-radius: 4px; }}
        .error {{ background: #fee; border-color: #e74c3c; }}
        .warning {{ background: #ffeaa7; border-color: #f39c12; }}
        .info {{ background: #e3f2fd; border-color: #3498db; }}
        .score {{ font-size: 48px; font-weight: bold; text-align: center; margin: 20px 0; }}
        .score.excellent {{ color: #27ae60; }}
        .score.good {{ color: #f39c12; }}
        .score.poor {{ color: #e74c3c; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .summary-item {{ text-align: center; }}
        .summary-number {{ font-size: 32px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>تقرير فحص الكود</h1>
        <p><strong>الملف:</strong> {os.path.basename(self.filepath)}</p>
        <p><strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <h2>الإحصائيات</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div>إجمالي الأسطر</div>
                    <div class="stat-value">{self.stats['lines']}</div>
                </div>
                <div class="stat-item">
                    <div>عدد الدوال</div>
                    <div class="stat-value">{self.stats['functions']}</div>
                </div>
                <div class="stat-item">
                    <div>عدد الكلاسات</div>
                    <div class="stat-value">{self.stats['classes']}</div>
                </div>
                <div class="stat-item">
                    <div>متوسط التعقيد</div>
                    <div class="stat-value">{self.stats['complexity'] / max(self.stats['functions'], 1):.1f}</div>
                </div>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-number" style="color: #e74c3c;">{len(errors)}</div>
                <div>أخطاء</div>
            </div>
            <div class="summary-item">
                <div class="summary-number" style="color: #f39c12;">{len(warnings)}</div>
                <div>تحذيرات</div>
            </div>
            <div class="summary-item">
                <div class="summary-number" style="color: #3498db;">{len(infos)}</div>
                <div>ملاحظات</div>
            </div>
        </div>
        
        <div class="score {'excellent' if score >= 90 else 'good' if score >= 70 else 'poor'}">
            {score}/100
        </div>
        
        <h2>المشاكل المكتشفة</h2>
"""
        
        if not self.issues:
            html += '<p style="color: #27ae60; font-size: 18px;">✓ لم يتم اكتشاف أي مشاكل!</p>'
        else:
            for issue in errors:
                html += f'<div class="issue error"><strong>[خطأ]</strong> السطر {issue["line"]}: {issue["msg"]}</div>\n'
            for issue in warnings:
                html += f'<div class="issue warning"><strong>[تحذير]</strong> السطر {issue["line"]}: {issue["msg"]}</div>\n'
            for issue in infos:
                html += f'<div class="issue info"><strong>[ملاحظة]</strong> السطر {issue["line"]}: {issue["msg"]}</div>\n'
        
        html += """
    </div>
</body>
</html>"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(color_text(f"\n✓ تم حفظ التقرير في: {output_file}", Fore.GREEN))

def check_directory(dirpath, export_format=None):
    print(color_text(f"فحص المجلد: {dirpath}", Fore.CYAN))
    print()
    
    py_files = list(Path(dirpath).rglob('*.py'))
    
    if not py_files:
        print(color_text("لم يتم العثور على ملفات Python في هذا المجلد", Fore.YELLOW))
        return
    
    print(f"تم العثور على {color_text(str(len(py_files)), Fore.CYAN)} ملف")
    print()
    
    total_issues = 0
    results = []
    
    for filepath in py_files:
        checker = CodeChecker(str(filepath))
        checker.analyze()
        
        if checker.issues:
            total_issues += len(checker.issues)
            results.append({
                'file': str(filepath.name),
                'issues': len(checker.issues)
            })
    
    results.sort(key=lambda x: x['issues'], reverse=True)
    
    for result in results[:10]:
        color = Fore.RED if result['issues'] > 10 else Fore.YELLOW if result['issues'] > 5 else Fore.BLUE
        print(f"- {result['file']}: {color_text(str(result['issues']), color)} مشكلة")
    
    if len(results) > 10:
        print(color_text(f"... و {len(results) - 10} ملف آخر", Fore.BLUE))
    
    print()
    print(f"إجمالي المشاكل: {color_text(str(total_issues), Fore.CYAN)}")

def print_logo():
    logo = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║     ██████  ██████  ████████  ███████             ║
    ║    ██      ██    ██ ██     ██ ██                  ║
    ║    ██      ██    ██ ██     ██ █████               ║
    ║    ██      ██    ██ ██     ██ ██                  ║
    ║     ██████  ██████  ████████  ███████             ║
    ║                                                   ║
    ║     ██████ ██   ██ ███████  ██████ ██   ██        ║
    ║    ██      ██   ██ ██      ██      ██  ██         ║
    ║    ██      ███████ █████   ██      █████          ║
    ║    ██      ██   ██ ██      ██      ██  ██         ║
    ║     ██████ ██   ██ ███████  ██████ ██   ██        ║
    ║                                                   ║
    ║               -= by Rlk-code =-                   ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    print(color_text(logo, Fore.CYAN))

def main():
    print_logo()
    
    if len(sys.argv) < 2:
        print(color_text("Code Quality Checker v1.0", Fore.CYAN))
        print()
        print("الاستخدام:")
        print("  python checker.py <file.py>              # لفحص ملف واحد")
        print("  python checker.py <directory>            # لفحص مجلد")
        print("  python checker.py <file.py> --json       # تصدير JSON")
        print("  python checker.py <file.py> --html       # تصدير HTML")
        sys.exit(1)
    
    target = sys.argv[1]
    export_format = None
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--json':
            export_format = 'json'
        elif sys.argv[2] == '--html':
            export_format = 'html'
    
    if os.path.isfile(target):
        checker = CodeChecker(target)
        total, empty, comments = checker.analyze()
        checker.print_report(total, empty, comments)
        
        if export_format == 'json':
            output = target.replace('.py', '_report.json')
            checker.export_json(output)
        elif export_format == 'html':
            output = target.replace('.py', '_report.html')
            checker.export_html(output)
            
    elif os.path.isdir(target):
        check_directory(target, export_format)
    else:
        print(color_text(f"خطأ: {target} غير موجود", Fore.RED))
        sys.exit(1)

if __name__ == '__main__':
    main()