from django.urls import path
from home import views, auth_views

app_name = 'home'

urlpatterns = [
    # Main pages
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('generate/', views.generate_journey, name='generate_journey'),
    path('demo/<slug:demo_slug>/', views.demo_journey, name='demo_journey'),
    path('journey/<int:topic_id>/', views.journey_view, name='journey'),
    path('quiz/<int:topic_id>/<int:scene_number>/', views.quiz_view, name='quiz'),
    path('certificate/<int:topic_id>/', views.certificate, name='certificate'),
    
    # API endpoints
    path('submit-quiz/<int:topic_id>/<int:scene_number>/', views.submit_quiz, name='submit_quiz'),
    path('regenerate/<int:topic_id>/<int:scene_number>/', views.regenerate_scene, name='regenerate_scene'),
    path('owl-chat/', views.owl_chat, name='owl_chat'),
    
    # Authentication
    path('auth/login/', auth_views.simple_login, name='simple_login'),
    path('auth/logout/', views.logout_view, name='logout'),
]
