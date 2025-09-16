from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('register/', views.user_register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password management
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        success_url='/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Quiz URLs
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:history_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),

    path("quizzes/", views.quiz_list, name="quiz_list"),
    path('generate-ai-quiz/', views.generate_ai_quiz, name='generate_ai_quiz'),
    path("quiz/<int:quiz_id>/take/", views.take_quiz, name="take_quiz"),
    path("quiz/review/<int:history_id>/", views.quiz_review, name="quiz_review"),
    #path('quizzes/', views.quiz_list, name='quiz_list'),
    path('ai-quiz-results/', views.ai_quiz_results, name='ai_quiz_results'),
    
    path('quiz/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('ai-quiz-results/', views.ai_quiz_results, name='ai_quiz_results'),
    # ... other patterns
    path('quiz/', views.quiz_list, name='quiz_list'),
    
    # Alternative using Class-Based View:
    # path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    
    # AJAX endpoint for subcategories
    path('ajax/subcategories/', views.get_subcategories, name='get_subcategories'),
    
    # Quiz generation endpoint (your existing view)
    path('ajax/generate-quiz/', views.GenerateQuizView.as_view(), name='generate_quiz'),
    
    # Quiz taking page
    path('quiz/take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    
    # Quiz detail/edit page (optional)
    path('quiz/detail/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    
    # Submit quiz answers
    path('quiz/submit/', views.submit_quiz, name='submit_quiz'),

     path('quiz/', views.quiz_list, name='quiz_list'),
    
    # AJAX endpoint for subcategories
    path('ajax/subcategories/', views.get_subcategories, name='get_subcategories'),
    
    # Quiz generation endpoint
    path('ajax/generate-quiz/', views.GenerateQuizView.as_view(), name='generate_quiz'),
    path('quiz/', views.quiz_list, name='quiz_list'),
    
    # AJAX endpoint for subcategories
    path('ajax/subcategories/', views.get_subcategories, name='get_subcategories'),
    
    # Quiz generation endpoint
    path('ajax/generate-quiz/', views.GenerateQuizView.as_view(), name='generate_quiz'),
]


