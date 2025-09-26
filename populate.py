import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_app.settings')
import django
django.setup()
from tracker.models import Month, Week, Day
from datetime import datetime, timedelta

# مسح البيانات
Day.objects.all().delete()
Week.objects.all().delete()
Month.objects.all().delete()

# الأشهر
months_data = [
    {"name": "أكتوبر 2025", "year": 2025, "number": 10},
    {"name": "نوفمبر 2025", "year": 2025, "number": 11},
    {"name": "ديسمبر 2025", "year": 2025, "number": 12},
    {"name": "يناير 2026", "year": 2026, "number": 1},
    {"name": "فبراير 2026", "year": 2026, "number": 2},
    {"name": "مارس 2026", "year": 2026, "number": 3},
    {"name": "أبريل 2026", "year": 2026, "number": 4},
    {"name": "مايو 2026", "year": 2026, "number": 5},
    {"name": "يونيو 2026", "year": 2026, "number": 6},
    {"name": "يوليو 2026", "year": 2026, "number": 7},
    {"name": "أغسطس 2026", "year": 2026, "number": 8},
    {"name": "سبتمبر 2026", "year": 2026, "number": 9},
    {"name": "أكتوبر 2026", "year": 2026, "number": 10},
]

for data in months_data:
    Month.objects.create(**data)

print("تم إضافة 13 شهر.")

# الأسابيع (4/شهر)
for month in Month.objects.all():
    for num in range(1, 5):
        Week.objects.create(month=month, number=num)

print("تم إضافة الأسابيع.")

# الأيام (7 أيام كاملة/أسبوع، من 1/10/2025)
start_date = datetime(2025, 10, 1).date()
week_counter = 0
for month in Month.objects.all():
    for week in month.week_set.all():
        for day_offset in range(7):  # 7 أيام
            day_date = start_date + timedelta(days=week_counter * 7 + day_offset)
            Day.objects.get_or_create(week=week, date=day_date)  # get_or_create للمرونة
        week_counter += 1

print(f"تم إضافة {Day.objects.count()} يوم (7/أسبوع). أول يوم: {Day.objects.first().date}.")
print("جاهز!") 



