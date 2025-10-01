from django.db.models import Sum, F, Q
from django.db.models import ExpressionWrapper, FloatField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Month, Week, Day, Code, Image, Note, EnglishNote
from datetime import date, datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
def home(request):
    months = Month.objects.all()
    return render(request, 'tracker/home.html', {'months': months})

def month_detail(request, month_id):
    month = get_object_or_404(Month, id=month_id)
    weeks = month.week_set.all()
    return render(request, 'tracker/month_detail.html', {'month': month, 'weeks': weeks})

def week_detail(request, week_id):
    week = get_object_or_404(Week, id=week_id)
    days = week.day_set.all().order_by('date')
    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        if new_date:
            new_day = Day.objects.create(week=week, date=datetime.strptime(new_date, '%Y-%m-%d').date())
            return redirect('week_detail', week_id=week.id)
    return render(request, 'tracker/week_detail.html', {'week': week, 'days': days})

def day_detail(request, day_id=None):
    if day_id:
        day = get_object_or_404(Day, id=day_id)
    else:
        search_date = request.GET.get('date')
        if search_date:
            day = get_object_or_404(Day, date=search_date)
            return redirect('day_detail', day_id=day.id)
        day = Day.objects.first()

    cyber_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    english_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    if request.method == 'POST':
        # التحقق من نوع النموذج بناءً على الحقول المرسلة
        if 'delete_code' in request.POST:
            code = get_object_or_404(Code, id=request.POST.get('delete_code'), day=day)
            code.delete()
        elif 'delete_image' in request.POST:
            image = get_object_or_404(Image, id=request.POST.get('delete_image'), day=day)
            image.delete()
        elif 'delete_note' in request.POST:
            note = get_object_or_404(Note, id=request.POST.get('delete_note'), day=day)
            note.delete()
        elif 'delete_english_note' in request.POST:
            english_note = get_object_or_404(EnglishNote, id=request.POST.get('delete_english_note'), day=day)
            english_note.delete()
        else:
            # تحديث الساعات فقط إذا كانت موجودة في الطلب (نموذج الساعات)
            if 'cyber_hours' in request.POST and 'english_hours' in request.POST:
                day.cyber_hours = float(request.POST.get('cyber_hours', day.cyber_hours))
                day.english_hours = float(request.POST.get('english_hours', day.english_hours))
                day.save()

            # إضافة كود إذا تم إرسال الحقول الخاصة به
            if 'add_code' in request.POST and 'code_title' in request.POST and request.POST['code_title']:
                Code.objects.create(day=day, title=request.POST['code_title'], content=request.POST['code_content'])

            # إضافة صورة إذا تم إرسال الحقول الخاصة بها
            if 'add_image' in request.POST and 'image_title' in request.POST and request.FILES.get('image_file'):
                Image.objects.create(day=day, title=request.POST['image_title'], file=request.FILES['image_file'])

            # إضافة مذكرة إذا تم إرسال الحقول الخاصة بها
            if 'add_note' in request.POST and 'note_title' in request.POST and request.POST['note_title']:
                Note.objects.create(day=day, title=request.POST['note_title'], content=request.POST['note_content'])

            # إضافة مذكرة إنجليزي إذا تم إرسال الحقول الخاصة بها
            if 'add_english_note' in request.POST and 'english_title' in request.POST and request.POST['english_title']:
                EnglishNote.objects.create(day=day, title=request.POST['english_title'], content=request.POST['english_content'])

        # تحديث النجوم بعد أي تغيير
        day.calculate_star()
        week = day.week
        week.stars = week.day_set.filter(star=True).count() * 3
        week.save()
        month = week.month
        month.stars = month.week_set.aggregate(total=Sum('stars'))['total'] or 0
        month.save()
        return redirect('day_detail', day_id=day.id)

    return render(request, 'tracker/day_detail.html', {
        'day': day,
        'cyber_options': cyber_options,
        'english_options': english_options
    })

@csrf_exempt
def add_study_day(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            study_date = data.get('study_date')
            cyber_hours = float(data.get('cyber_hours', 0))
            english_hours = float(data.get('english_hours', 0))
            
            study_date_obj = datetime.strptime(study_date, '%Y-%m-%d').date()
            month = Month.objects.filter(number=study_date_obj.month, year=study_date_obj.year).first()
            if not month:
                return JsonResponse({'success': False, 'error': 'لم يتم العثور على شهر مطابق'}, status=400)
            week_number = (study_date_obj.day - 1) // 7 + 1
            week = Week.objects.filter(month=month, number=week_number).first()
            if not week:
                return JsonResponse({'success': False, 'error': 'لم يتم العثور على أسبوع مطابق'}, status=400)
            
            day, created = Day.objects.get_or_create(
                date=study_date_obj,
                week=week,
                defaults={'cyber_hours': cyber_hours, 'english_hours': english_hours}
            )
            if not created:
                day.cyber_hours = cyber_hours
                day.english_hours = english_hours
                day.save()
            
            day.calculate_star()
            week.stars = week.day_set.filter(star=True).count() * 3
            week.save()
            month.stars = month.week_set.aggregate(total=Sum('stars'))['total'] or 0
            month.save()
            
            return JsonResponse({
                'success': True,
                'day_id': day.id,
                'total_hours': cyber_hours + english_hours,
                'stars': 3 if day.star else 0,
                'event': {
                    'title': f'ساعات: {cyber_hours + english_hours:.1f} | {"⭐" if day.star else "❌"}',
                    'start': study_date,
                    'url': f'/day/{day.id}/',
                    'backgroundColor': '#28a745' if day.star else '#dc3545'
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'الطريقة غير صالحة'}, status=405)

def stats(request):
    total_hours_agg = Day.objects.aggregate(cyber=Sum('cyber_hours'), english=Sum('english_hours'))
    studied_hours = (total_hours_agg['cyber'] or 0) + (total_hours_agg['english'] or 0)
    total_stars = Day.objects.filter(star=True).count() * 3
    studied_days_count = Day.objects.filter(cyber_hours__gt=0).count()
    search_query = request.GET.get('search', '')
    items = []
    if search_query:
        codes = Code.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        images = Image.objects.filter(title__icontains=search_query)
        notes = Note.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        english_notes = EnglishNote.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        items = list(codes) + list(images) + list(notes) + list(english_notes)
        for item in items:
            item.item_type = 'كود' if isinstance(item, Code) else 'صورة' if isinstance(item, Image) else 'مذكرة' if isinstance(item, Note) else 'ملاحظة إنجليزية'
    
    months = Month.objects.all()
    monthly_data = []
    for month in months:
        month_cyber = Day.objects.filter(week__month=month).aggregate(total=Sum('cyber_hours'))['total'] or 0
        month_english = Day.objects.filter(week__month=month).aggregate(total=Sum('english_hours'))['total'] or 0
        month_stars = month.stars or 0
        month_days = Day.objects.filter(week__month=month, cyber_hours__gt=0).count()
        monthly_data.append({
            'name': month.name,
            'cyber_hours': month_cyber,
            'english_hours': month_english,
            'stars': month_stars,
            'days': month_days
        })
    
    weak_days = Day.objects.annotate(
        total_hours=ExpressionWrapper(F('cyber_hours') + F('english_hours'), output_field=FloatField())
    ).filter(total_hours__lt=3, cyber_hours__gt=0).order_by('-date')
    
    start_date = datetime(2025, 10, 1).date()
    end_date = datetime(2026, 10, 1).date()
    today = date.today()
    total_days = (end_date - start_date).days
    days_passed = max(0, (today - start_date).days)
    time_progress = (days_passed / total_days) * 100 if total_days > 0 else 0
    total_possible_hours = 1560
    total_possible_stars = 468
    total_possible_days = total_days
    remaining_hours = total_possible_hours - studied_hours
    remaining_stars = total_possible_stars - total_stars
    remaining_days = total_possible_days - studied_days_count
    hours_progress = min(100, (studied_hours / total_possible_hours) * 100)
    stars_progress = min(100, (total_stars / total_possible_stars) * 100)
    days_progress = min(100, (studied_days_count / total_possible_days) * 100)
    
    alert_message = "تقدمك أقل من 50%! حاول تزود مجهودك 🚀" if hours_progress < 50 else None
    
    return render(request, 'tracker/stats.html', {
        'studied_hours': studied_hours,
        'total_stars': total_stars,
        'studied_days_count': studied_days_count,
        'items': items,
        'search_query': search_query,
        'time_progress': time_progress,
        'hours_progress': hours_progress,
        'stars_progress': stars_progress,
        'days_progress': days_progress,
        'days_passed': days_passed,
        'total_possible_hours': total_possible_hours,
        'total_possible_stars': total_possible_stars,
        'total_possible_days': total_possible_days,
        'remaining_hours': remaining_hours,
        'remaining_stars': remaining_stars,
        'remaining_days': remaining_days,
        'monthly_data': monthly_data,
        'weak_days': weak_days,
        'alert_message': alert_message,
    })

def content(request):
    studied_days = Day.objects.filter(cyber_hours__gt=0).select_related('week__month').order_by('-date')
    codes = Code.objects.all().select_related('day')
    images = Image.objects.all().select_related('day')
    notes = Note.objects.all().select_related('day')
    english_notes = EnglishNote.objects.all().select_related('day')
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    search_results = []
    if search_query:
        days = Day.objects.filter(date__icontains=search_query, cyber_hours__gt=0)
        codes = Code.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        images = Image.objects.filter(title__icontains=search_query)
        notes = Note.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        english_notes = EnglishNote.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
        
        if type_filter == 'day':
            search_results = list(days)
        elif type_filter == 'code':
            search_results = list(codes)
        elif type_filter == 'image':
            search_results = list(images)
        elif type_filter == 'note':
            search_results = list(notes)
        elif type_filter == 'english_note':
            search_results = list(english_notes)
        else:
            search_results = list(days) + list(codes) + list(images) + list(notes) + list(english_notes)
        
        for item in search_results:
            item.item_type = (
                'يوم' if isinstance(item, Day) else
                'كود' if isinstance(item, Code) else
                'صورة' if isinstance(item, Image) else
                'مذكرة' if isinstance(item, Note) else
                'ملاحظة إنجليزية'
            )
            item.content = (
                f'ساعات: {item.cyber_hours + item.english_hours:.1f}' if isinstance(item, Day) else
                item.content if hasattr(item, 'content') else
                item.file.url if isinstance(item, Image) else ''
            )
            item.title = (
                item.date.strftime('%d/%m/%Y') if isinstance(item, Day) else
                item.title
            )
    
    if request.method == 'POST':
        if 'delete_code' in request.POST:
            code = get_object_or_404(Code, id=request.POST.get('delete_code'))
            code.delete()
        elif 'delete_image' in request.POST:
            image = get_object_or_404(Image, id=request.POST.get('delete_image'))
            image.delete()
        elif 'delete_note' in request.POST:
            note = get_object_or_404(Note, id=request.POST.get('delete_note'))
            note.delete()
        elif 'delete_english_note' in request.POST:
            english_note = get_object_or_404(EnglishNote, id=request.POST.get('delete_english_note'))
            english_note.delete()
        return redirect('content')
    
    return render(request, 'tracker/content.html', {
        'studied_days': studied_days,
        'codes': codes[:6],
        'more_codes': codes[6:],
        'images': images[:6],
        'more_images': images[6:],
        'notes': notes[:6],
        'more_notes': notes[6:],
        'english_notes': english_notes[:6],
        'more_english_notes': english_notes[6:],
        'search_query': search_query,
        'search_results': search_results,
        'type_filter': type_filter,
    })

def edit_code(request, code_id):
    code = get_object_or_404(Code, id=code_id)
    if request.method == 'POST':
        code.title = request.POST.get('code_title')
        code.content = request.POST.get('code_content')
        code.save()
        return redirect('content')
    return render(request, 'tracker/edit_code.html', {'code': code})

def edit_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    if request.method == 'POST':
        image.title = request.POST.get('image_title')
        if request.FILES.get('image_file'):
            image.file = request.FILES['image_file']
        image.save()
        return redirect('content')
    return render(request, 'tracker/edit_image.html', {'image': image})

def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title:  # التأكد من أن title ليس فارغًا
            note.title = title
            note.content = content
            note.save()
            return redirect('content')
        else:
            # إرجاع رسالة خطأ إذا كان العنوان فارغًا
            return render(request, 'tracker/edit_note.html', {
                'note': note,
                'error': 'حقل العنوان مطلوب ولا يمكن أن يكون فارغًا'
            })
    return render(request, 'tracker/edit_note.html', {'note': note})

def edit_english_note(request, english_note_id):
    english_note = get_object_or_404(EnglishNote, id=english_note_id)
    if request.method == 'POST':
        english_note.title = request.POST.get('english_title')
        english_note.content = request.POST.get('english_content')
        english_note.save()
        return redirect('content')
    return render(request, 'tracker/edit_english_note.html', {'english_note': english_note})

@csrf_exempt
def delete_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_type = data.get('item_type')
            item_id = data.get('item_id')
            if item_type == 'code':
                item = get_object_or_404(Code, id=item_id)
            elif item_type == 'image':
                item = get_object_or_404(Image, id=item_id)
            elif item_type == 'note':
                item = get_object_or_404(Note, id=item_id)
            elif item_type == 'english_note':
                item = get_object_or_404(EnglishNote, id=item_id)
            else:
                return JsonResponse({'success': False, 'error': 'نوع غير صالح'})
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'الطريقة غير صالحة'}, status=405)

def calendar(request):
    days = Day.objects.all().select_related('week__month')
    events = []
    for day in days:
        if day.cyber_hours > 0 or day.english_hours > 0:  # الأيام المدروسة فقط
            total_hours = day.cyber_hours + day.english_hours
            events.append({
                'title': f"{total_hours:.1f} ساعات | {'⭐' if day.star else '❌'}",
                'start': day.date.isoformat(),
                'url': reverse('day_detail', args=[day.id]),
                'backgroundColor': '#28a745' if day.star else '#dc3545',
                'borderColor': 'darkgreen' if day.star else 'darkred',
            })
    
    context = {
        'events_json': json.dumps(events)
    }
    return render(request, 'tracker/calendar.html', context)