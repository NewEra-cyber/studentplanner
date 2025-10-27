from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_page, name='profile'),
    
    # Timetable management
    path('timetable/', views.timetable_input, name='timetable_input'),
    path('timetable/delete/<uuid:entry_id>/', views.delete_timetable_entry, name='delete_timetable_entry'),
    path('timetable/generate-schedule/', views.generate_schedule_from_timetable, name='generate_schedule_from_timetable'),
    path('timetable/clear/', views.clear_timetable, name='clear_timetable'),
    
    # Activities management
    path('activities/', views.manage_activities, name='manage_activities'),
    
    # Resources pages
    path('activities/resources/', views.activities_resources, name='activities_resources'),
    path('resources/<uuid:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resources/<uuid:resource_id>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('resources/category/<uuid:category_id>/', views.resource_by_category, name='resource_by_category'),
    path('resources/activity-type/<str:activity_type>/', views.resource_by_activity_type, name='resource_by_activity_type'),
    path('resources/my-favorites/', views.my_favorites, name='my_favorites'),
    path('resources/search/', views.search_resources, name='search_resources'),
    
    # Class Notes URLs
    path('class-notes/', views.class_notes, name='class_notes'),
    path('class-notes/create-folder/', views.create_folder, name='create_folder'),
    path('class-notes/upload-file/', views.upload_file, name='upload_file'),
    path('class-notes/create-file/', views.create_file, name='create_file'),
    path('class-notes/get-folder-content/', views.get_folder_content, name='get_folder_content'),
    path('class-notes/get-file-content/', views.get_file_content, name='get_file_content'),
    path('class-notes/generate-summary/', views.generate_summary, name='generate_summary'),
    path('class-notes/launch-vscode/', views.launch_vscode, name='launch_vscode'),
    
    # Manual schedule adjustment
    path('adjust-schedule/', views.adjust_schedule_manual, name='adjust_schedule'),

    # Theme toggle
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
]