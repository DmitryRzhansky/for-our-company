from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note_list'),
    path('project-notes/', views.ProjectNoteListView.as_view(), name='project_note_list'),
    path('project/<slug:slug>/', views.project_detail_enhanced, name='project_detail_enhanced'),
    path('project/<slug:slug>/checklists/', views.project_checklists, name='project_checklists'),
    path('checklist/<int:checklist_id>/', views.checklist_detail, name='checklist_detail'),
    path('checklist-item/<int:item_id>/toggle/', views.toggle_checklist_item, name='toggle_checklist_item'),
    path('checklist/<int:checklist_id>/add-item/', views.add_checklist_item, name='add_checklist_item'),
]
