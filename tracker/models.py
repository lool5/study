from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Month(models.Model):
    number = models.IntegerField()
    year = models.IntegerField(default=2025)
    name = models.CharField(max_length=50)
    stars = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Week(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    number = models.IntegerField()
    stars = models.IntegerField(default=0)

    def __str__(self):
        return f"أسبوع {self.number} في {self.month}"

class Day(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    cyber_hours = models.FloatField(default=0)
    english_hours = models.FloatField(default=0)
    star = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date)

    def calculate_star(self):
        has_code = self.codes.exists()
        has_image = self.images.exists()
        has_note = self.notes.exists()
        has_english_note = self.english_notes.exists()
        total_hours = self.cyber_hours + self.english_hours
        self.star = has_code and has_image and has_note and has_english_note and total_hours >= 10
        self.save()

class Code(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='codes')
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title

class Image(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=100)
    file = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title

class Note(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title

class EnglishNote(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='english_notes')
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title



class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # اختياري لو في تسجيل دخول
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Question: {self.question[:50]}..."




class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان المهمة")
    description = models.TextField(blank=True, verbose_name="وصف المهمة")
    due_date = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإضافة")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")
    is_completed = models.BooleanField(default=False, verbose_name="منجزة؟")

    def __str__(self):
        return self.title

    def is_overdue(self):
        if not self.is_completed and self.due_date < timezone.now():
            return True
        return False

    def completion_delay(self):
        if self.is_completed and self.completed_at:
            delay = self.completed_at - self.due_date
            if delay.days > 0:
                return f"متأخر بـ {delay.days} يوم"
            else:
                return f"منجز قبل المعاد بـ {-delay.days} يوم"
        return "غير منجزة"

    def time_taken(self):
        if self.is_completed and self.completed_at:
            time_taken = self.completed_at - self.created_at
            return f"تم الإكمال بعد {time_taken.days} يوم من الإضافة"
        return "غير منجزة"
