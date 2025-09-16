from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Sub Categories"
        unique_together = ('category', 'name')
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='quizzes')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='quizzes', blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    time_limit = models.IntegerField(help_text="Time limit in minutes", validators=[MinValueValidator(1)])
    total_marks = models.IntegerField(validators=[MinValueValidator(1)])
    pass_marks = models.IntegerField(validators=[MinValueValidator(1)])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_ai_generated = models.BooleanField(default=False)
    ai_topic = models.CharField(max_length=200, blank=True, null=True, help_text="Topic used for AI generation")
    ai_instructions = models.TextField(blank=True, null=True, help_text="Special instructions for AI generation")
    generation_metadata = models.JSONField(default=dict, blank=True, help_text="Store AI generation details")
    class Meta:
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return self.title
    
    def get_questions_count(self):
        return self.questions.count()


class Question(models.Model):
    QUESTION_TYPES = [
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    options = models.JSONField(default=list, help_text="Store options as JSON list")
    correct_answers = models.JSONField(default=list, help_text="Store correct answer indices as JSON list")
    marks = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    explanation = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.quiz.title} - Question {self.order}"
    
    def get_options(self):
        """Return options as a list"""
        if isinstance(self.options, str):
            return json.loads(self.options)
        return self.options
    
    def get_correct_answers(self):
        """Return correct answers as a list"""
        if isinstance(self.correct_answers, str):
            return json.loads(self.correct_answers)
        return self.correct_answers


class QuizHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_histories')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='histories')
    score = models.IntegerField()
    total_marks = models.IntegerField()
    percentage = models.FloatField()
    time_taken = models.IntegerField(help_text="Time taken in minutes")
    passed = models.BooleanField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Quiz Histories"
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total_marks})"


class UserAnswer(models.Model):
    quiz_history = models.ForeignKey(QuizHistory, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.JSONField(default=list, help_text="Store selected answer indices as JSON list")
    is_correct = models.BooleanField()
    marks_obtained = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('quiz_history', 'question')
    
    def __str__(self):
        return f"{self.quiz_history.user.username} - {self.question.quiz.title} - Q{self.question.order}"
    
    def get_selected_answers(self):
        """Return selected answers as a list"""
        if isinstance(self.selected_answers, str):
            return json.loads(self.selected_answers)
        return self.selected_answers


# User Profile Extension (Optional)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"