from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/download/', views.project_download_all, name='project_download_all'),
    path('<slug:slug>/content/<int:content_id>/', views.content_view, name='content_view'),
]
