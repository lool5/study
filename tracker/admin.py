from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Month, Week, Day, Code, Image, Note, EnglishNote

admin.site.register(Month)
admin.site.register(Week)
admin.site.register(Day)
admin.site.register(Code)
admin.site.register(Image)
admin.site.register(Note)
admin.site.register(EnglishNote)