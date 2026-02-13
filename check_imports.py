try:
    import openpyxl
    print("openpyxl: OK")
except ImportError:
    print("openpyxl: MISSING")

try:
    import docx
    print("python-docx: OK")
except ImportError:
    print("python-docx: MISSING")
