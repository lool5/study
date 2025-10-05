from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_page, name='chat_page'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('clear_chat/', views.clear_chat, name='clear_chat'),
    path('month/<int:month_id>/', views.month_detail, name='month_detail'),
    path('week/<int:week_id>/', views.week_detail, name='week_detail'),
    path('day/<int:day_id>/', views.day_detail, name='day_detail'),
    path('day/', views.day_detail, name='day_detail'),
    path('stats/', views.stats, name='stats'),
    path('content/', views.content, name='content'),
    path('edit/code/<int:code_id>/', views.edit_code, name='edit_code'),
    path('edit/image/<int:image_id>/', views.edit_image, name='edit_image'),
    path('edit/note/<int:note_id>/', views.edit_note, name='edit_note'),
    path('edit/english_note/<int:english_note_id>/', views.edit_english_note, name='edit_english_note'),
    path('api/add-study-day/', views.add_study_day, name='add_study_day'),
    path('api/delete-item/', views.delete_item, name='delete_item'),
    path('calendar/', views.calendar, name='calendar'),
]

