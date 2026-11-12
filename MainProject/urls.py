from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from Readora import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search-books/', views.search_books, name='search_books'),
    path('issue-books/', views.issue_books, name='issue_books'),
    path('reminders/', views.reminders, name='reminders'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # APIs & Modern LMS Features
    path('api/isbn-lookup/', views.api_isbn_lookup, name='api_isbn_lookup'),
    path('receipt/<int:record_id>/', views.download_receipt, name='download_receipt'),

    # Guarantee static files (PDFs, CSS, Images) always serve in production on Vercel
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
