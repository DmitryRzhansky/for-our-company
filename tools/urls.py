from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    # Основные инструменты
    path('', views.BasicAnalysisListView.as_view(), name='analysis_list'),
    path('websites/', views.WebsiteListView.as_view(), name='website_list'),
    path('websites/<int:pk>/', views.WebsiteDetailView.as_view(), name='website_detail'),
    path('analyses/', views.BasicAnalysisListView.as_view(), name='analysis_list'),
    path('analyses/<int:pk>/', views.BasicAnalysisDetailView.as_view(), name='analysis_detail'),
    path('analyze/', views.analyze_website, name='analyze_website'),
    path('export/', views.export_to_excel, name='export_excel'),
    path('analysis/<int:analysis_id>/robots.txt', views.download_robots_txt, name='download_robots'),
    path('analysis/<int:analysis_id>/sitemap.xml', views.download_sitemap_xml, name='download_sitemap'),
    
]
