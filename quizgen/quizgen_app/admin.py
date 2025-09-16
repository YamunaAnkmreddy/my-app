from django.contrib import admin
from .models import Category, SubCategory, Quiz, Question, QuizHistory, UserAnswer, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'created_at']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'marks', 'order']


"""@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'subcategory', 'difficulty', 'total_marks', 'pass_marks', 'is_active', 'created_at']
    search_fields = ['title', 'category__name', 'subcategory__name']
    list_filter = ['category', 'subcategory', 'difficulty', 'is_active', 'created_at']
    inlines = [QuestionInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new quiz
            obj.created_by = request.user
        super().save_model(request, obj, form, change)"""


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_text', 'question_type', 'marks', 'order']
    search_fields = ['question_text', 'quiz__title']
    list_filter = ['quiz', 'question_type']
    ordering = ['quiz', 'order']


@admin.register(QuizHistory)
class QuizHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'total_marks', 'percentage', 'passed', 'completed_at']
    search_fields = ['user__username', 'quiz__title']
    list_filter = ['passed', 'quiz', 'completed_at']
    readonly_fields = ['completed_at']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['quiz_history', 'question', 'is_correct', 'marks_obtained']
    search_fields = ['quiz_history__user__username', 'question__question_text']
    list_filter = ['is_correct', 'question__quiz']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    list_filter = ['created_at']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'subcategory', 'difficulty', 'total_marks', 'pass_marks', 'is_active', 'is_ai_generated', 'created_at']
    search_fields = ['title', 'category__name', 'subcategory__name', 'ai_topic']
    list_filter = ['category', 'subcategory', 'difficulty', 'is_active', 'is_ai_generated', 'created_at']
    inlines = [QuestionInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new quiz
            obj.created_by = request.user
        super().save_model(request, obj, form, change)