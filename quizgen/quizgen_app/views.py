from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Avg, Count, Max
from django.core.paginator import Paginator
import json
from datetime import timedelta
from .ai_generator import AIQuizGenerator
import json
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Quiz, Question, QuizHistory, UserAnswer, Category, SubCategory, UserProfile
from .forms import UserRegisterForm, UserLoginForm, QuizForm, QuestionForm, QuizFilterForm, UserProfileForm


def home(request):
    """Home page view"""
    recent_quizzes = Quiz.objects.filter(is_active=True).order_by('-created_at')[:6]
    categories = Category.objects.all()[:8]
    
    # Statistics
    total_quizzes = Quiz.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    
    context = {
        'recent_quizzes': recent_quizzes,
        'categories': categories,
        'total_quizzes': total_quizzes,
        'total_categories': total_categories,
    }
    
    if request.user.is_authenticated:
        user_quiz_count = QuizHistory.objects.filter(user=request.user).count()
        context['user_quiz_count'] = user_quiz_count
    
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    """Dashboard view"""
    user = request.user
    
    # Statistics
    quiz_attempts = QuizHistory.objects.filter(user=user).count()
    passed_quizzes = QuizHistory.objects.filter(user=user, passed=True).count()
    average_score = QuizHistory.objects.filter(user=user).aggregate(
        avg_score=Avg('percentage'))['avg_score'] or 0
    
    # Recent history
    recent_history = QuizHistory.objects.filter(user=user).order_by('-completed_at')[:5]
    
    # Categories
    categories = Category.objects.all()
    
    context = {
        'quiz_attempts': quiz_attempts,
        'passed_quizzes': passed_quizzes,
        'average_score': average_score,
        'streak_days': 0,  # You can implement streak logic
        'categories': categories,
        'recent_history': recent_history,
    }
    
    return render(request, 'dashboard.html', context)


def user_register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view"""
    form_class = UserLoginForm
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'You have been logged in successfully!')
        return super().form_valid(form)


@login_required
def profile(request):
    """User profile view"""
    user = request.user
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=profile)
    
    # Statistics
    quiz_count = QuizHistory.objects.filter(user=user).count()
    passed_count = QuizHistory.objects.filter(user=user, passed=True).count()
    avg_score = QuizHistory.objects.filter(user=user).aggregate(
        avg=Avg('percentage'))['avg'] or 0
    
    # Recent activity
    recent_activity = QuizHistory.objects.filter(user=user).order_by('-completed_at')[:5]
    
    context = {
        'profile_form': profile_form,
        'quiz_count': quiz_count,
        'passed_count': passed_count,
        'avg_score': avg_score,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'registration/profile.html', context)


"""def quiz_list(request):
    Main quiz list view - handles both AI quiz generation and regular quiz display
    
    # Check if this is an AI quiz generation request
    category = request.GET.get("category")
    subcategory = request.GET.get("subcategory") 
    difficulty = request.GET.get("difficulty", "medium")
    topic = request.GET.get("topic")
    
    # If we have AI quiz parameters, generate AI quiz
    if category or subcategory or topic:
        try:
            # Generate AI quiz questions
            quiz_data = AIQuizGenerator.generate_quiz(
                category=category,
                subcategory=subcategory,
                difficulty=difficulty,
                num_questions=5,
                user=request.user if request.user.is_authenticated else None,
                topic=topic
            )

            # Process the quiz data for the template
            for q in quiz_data:
                # Create options list for easy template iteration
                q["options"] = [
                    q.get("option1", ""),
                    q.get("option2", ""), 
                    q.get("option3", ""),
                    q.get("option4", "")
                ]
                
                # Map correct answer letter to actual text
                answer_mapping = {
                    "A": q.get("option1", ""),
                    "B": q.get("option2", ""),
                    "C": q.get("option3", ""), 
                    "D": q.get("option4", "")
                }
                q["correct_answer_text"] = answer_mapping.get(q.get("correct_answer", ""), "")

            # Handle POST request (quiz submission)
            if request.method == "POST":
                return handle_ai_quiz_submission(request, quiz_data)

            context = {
                "quiz_data": quiz_data,
                "quiz_title": f"AI Generated Quiz - {topic or category or 'Mixed'}",
                "is_ai_quiz": True
            }
            
            return render(request, "quiz/quiz_list.html", context)
            
        except Exception as e:
            messages.error(request, f"Error generating AI quiz: {str(e)}")
            quiz_data = None
    
    # Regular quiz listing (fallback or default behavior)
    else:
        quizzes = Quiz.objects.filter(is_active=True).select_related('category', 'subcategory', 'created_by')
        
        # Apply filters
        form = QuizFilterForm(request.GET)
        if form.is_valid():
            if form.cleaned_data.get('category'):
                quizzes = quizzes.filter(category=form.cleaned_data['category'])
            
            if form.cleaned_data.get('difficulty'):
                quizzes = quizzes.filter(difficulty=form.cleaned_data['difficulty'])
            
            if form.cleaned_data.get('search'):
                search_query = form.cleaned_data['search']
                quizzes = quizzes.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__name__icontains=search_query)
                )

        # Pagination
        paginator = Paginator(quizzes, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'form': form,
            'total_quizzes': paginator.count,
            'is_ai_quiz': False,
            'quiz_data': None
        }
        
        return render(request, 'quiz/quiz_list.html', context)"""
def quiz_list(request):
    """
    Display list of all quizzes with filtering capabilities
    """
    try:
        # Get all quizzes with related data to avoid N+1 queries
        quizzes = Quiz.objects.select_related('category', 'subcategory').annotate(
            question_count=Count('questions')
        ).order_by('-id')  # Order by ID
        
        # Get all categories for the form and filters
        categories = Category.objects.all().prefetch_related('subcategory_set')
        
        # Optional: Apply filters from URL parameters
        category_filter = request.GET.get('category')
        difficulty_filter = request.GET.get('difficulty')
        subcategory_filter = request.GET.get('subcategory')
        
        if category_filter:
            try:
                quizzes = quizzes.filter(category_id=int(category_filter))
            except (ValueError, TypeError):
                pass  # Invalid category_filter, ignore
            
        if difficulty_filter and difficulty_filter.upper() in ['E', 'M', 'H']:
            quizzes = quizzes.filter(difficulty=difficulty_filter.upper())
            
        if subcategory_filter:
            try:
                quizzes = quizzes.filter(subcategory_id=int(subcategory_filter))
            except (ValueError, TypeError):
                pass  # Invalid subcategory_filter, ignore
        
        context = {
            'quizzes': quizzes,
            'categories': categories,
            'selected_category': category_filter,
            'selected_difficulty': difficulty_filter,
            'selected_subcategory': subcategory_filter,
        }
        
        return render(request, 'quizzes/quiz_list.html', context)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in quiz_list view: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a basic error response
        return render(request, 'quizzes/quiz_list.html', {
            'quizzes': Quiz.objects.none(),  # Empty queryset
            'categories': Category.objects.all(),
            'error_message': 'An error occurred while loading quizzes.'
        })


def get_subcategories(request):
    """
    AJAX view to get subcategories for a given category
    """
    if request.method == 'GET':
        category_id = request.GET.get('category_id')
        if category_id:
            try:
                category_id = int(category_id)
                subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
                return JsonResponse({
                    'success': True,
                    'subcategories': list(subcategories)
                })
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid category_id'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No category_id provided'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

def handle_ai_quiz_submission(request, quiz_data):
    """Handle AI quiz form submission"""
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to submit a quiz.")
        return redirect('login')
    
    user_answers = {}
    score = 0
    total_questions = len(quiz_data)
    
    # Process each question's answer
    for i, question in enumerate(quiz_data):
        question_key = f"question_{i}"
        selected_answer = request.POST.get(question_key)
        
        if selected_answer:
            user_answers[i] = {
                'selected': selected_answer,
                'correct': question.get('correct_answer_text', ''),
                'is_correct': selected_answer == question.get('correct_answer_text', '')
            }
            
            if user_answers[i]['is_correct']:
                score += 1
        else:
            user_answers[i] = {
                'selected': None,
                'correct': question.get('correct_answer_text', ''),
                'is_correct': False
            }
    
    # Calculate percentage
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Store results in session for review page
    request.session['quiz_results'] = {
        'quiz_data': quiz_data,
        'user_answers': user_answers,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'passed': percentage >= 60  # 60% pass mark
    }
    
    return redirect('ai_quiz_results')


@login_required
def ai_quiz_results(request):
    """Display AI quiz results"""
    quiz_results = request.session.get('quiz_results')
    
    if not quiz_results:
        messages.error(request, "No quiz results found.")
        return redirect('quiz_list')
    
    context = {
        'quiz_results': quiz_results,
        'show_explanations': True
    }
    
    return render(request, 'quiz/ai_quiz_results.html', context)


@login_required
def quiz_detail(request, quiz_id):
    """Quiz detail view"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Check if user has already taken this quiz
    user_history = QuizHistory.objects.filter(user=request.user, quiz=quiz).first()
    
    context = {
        'quiz': quiz,
        'user_history': user_history,
        'questions_count': quiz.get_questions_count(),
    }
    
    return render(request, 'quiz/quiz_detail.html', context)


@login_required
def take_quiz(request, quiz_id):
    """Take quiz view"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        # Process quiz submission
        return process_quiz_submission(request, quiz, questions)
    
    # Start quiz session
    request.session[f'quiz_{quiz_id}_start_time'] = timezone.now().isoformat()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'total_questions': questions.count(),
    }
    
    return render(request, 'quiz/take_quiz.html', context)


def process_quiz_submission(request, quiz, questions):
    """Process quiz submission and calculate results"""
    # Get start time from session
    start_time_str = request.session.get(f'quiz_{quiz.id}_start_time')
    if not start_time_str:
        messages.error(request, 'Quiz session expired. Please start again.')
        return redirect('quiz_detail', quiz_id=quiz.id)
    
    start_time = timezone.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    completed_time = timezone.now()
    time_taken = int((completed_time - start_time).total_seconds() / 60)  # in minutes
    
    # Calculate score
    total_score = 0
    total_marks = quiz.total_marks
    
    # Create quiz history
    quiz_history = QuizHistory.objects.create(
        user=request.user,
        quiz=quiz,
        score=0,  # Will update after processing answers
        total_marks=total_marks,
        percentage=0,  # Will update after processing answers
        time_taken=time_taken,
        passed=False,  # Will update after processing answers
        started_at=start_time,
    )
    
    # Process each question
    for question in questions:
        selected_answers = request.POST.getlist(f'question_{question.id}')
        selected_indices = [int(ans) for ans in selected_answers if ans.isdigit()]
        
        correct_answers = question.get_correct_answers()
        is_correct = set(selected_indices) == set(correct_answers)
        marks_obtained = question.marks if is_correct else 0
        
        # Create user answer
        UserAnswer.objects.create(
            quiz_history=quiz_history,
            question=question,
            selected_answers=selected_indices,
            is_correct=is_correct,
            marks_obtained=marks_obtained
        )
        
        if is_correct:
            total_score += marks_obtained
    
    # Update quiz history
    percentage = (total_score / total_marks) * 100 if total_marks > 0 else 0
    quiz_history.score = total_score
    quiz_history.percentage = percentage
    quiz_history.passed = total_score >= quiz.pass_marks
    quiz_history.save()
    
    # Clear session
    if f'quiz_{quiz.id}_start_time' in request.session:
        del request.session[f'quiz_{quiz.id}_start_time']
    
    return redirect('quiz_review', history_id=quiz_history.id)


@login_required
def quiz_result(request, history_id):
    """Quiz result view"""
    quiz_history = get_object_or_404(QuizHistory, id=history_id, user=request.user)
    user_answers = quiz_history.user_answers.select_related('question').order_by('question__order')
    
    context = {
        'quiz_history': quiz_history,
        'user_answers': user_answers,
    }
    
    return render(request, 'quiz/quiz_result.html', context)


@login_required
def quiz_history(request):
    """Quiz history view"""
    user = request.user
    history_list = QuizHistory.objects.filter(user=user).select_related('quiz', 'quiz__category').order_by('-completed_at')
    
    # Pagination
    paginator = Paginator(history_list, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_attempts = history_list.count()
    passed_attempts = history_list.filter(passed=True).count()
    average_score = history_list.aggregate(avg=Avg('percentage'))['avg'] or 0
    best_score = history_list.aggregate(best=Max('percentage'))['best'] or 0
    
    context = {
        'quiz_history': page_obj,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'average_score': average_score,
        'best_score': best_score,
    }
    
    return render(request, 'quiz/quiz_history.html', context)


def category_list(request):
    """Category list view"""
    categories = Category.objects.all().prefetch_related('subcategories', 'quizzes')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'categories/category_list.html', context)


def category_detail(request, category_id):
    """Category detail view with subcategories"""
    category = get_object_or_404(Category, id=category_id)
    quizzes = Quiz.objects.filter(category=category, is_active=True).select_related('subcategory')
    
    # Add questions count for category stats
    from .models import Question
    total_questions = Question.objects.filter(quiz__category=category).count()
    
    context = {
        'category': category,
        'quizzes': quizzes,
        'questions_count': total_questions,
    }
    
    return render(request, 'categories/category_detail.html', context)


@login_required
def generate_ai_quiz(request):
    """Generate AI quiz endpoint"""
    
    try:
        # Get form data
        topic = request.POST.get('topic', '').strip()
        num_questions = int(request.POST.get('num_questions', 10))
        difficulty = request.POST.get('difficulty', 'medium')
        instructions = request.POST.get('instructions', '').strip()
        
        # Validate input
        if not topic:
            return JsonResponse({
                'success': False,
                'error': 'Topic is required'
            })
        
        if num_questions < 1 or num_questions > 50:
            return JsonResponse({
                'success': False,
                'error': 'Number of questions must be between 1 and 50'
            })
        
        # Generate quiz using AI
        generator = AIQuizGenerator()
        quiz = generator.generate_quiz(
            topic=topic,
            num_questions=num_questions,
            difficulty=difficulty,
            instructions=instructions or None,
            user=request.user
        )
        
        return JsonResponse({
            'success': True,
            'quiz_id': quiz.id,
            'message': f'Successfully generated "{quiz.title}" with {num_questions} questions!'
        })
        
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'OpenAI API key not configured. Please contact administrator.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def quiz_review(request, history_id):
    """Review submitted quiz with highlighted answers"""
    quiz_history = get_object_or_404(QuizHistory, id=history_id, user=request.user)
    user_answers = UserAnswer.objects.filter(quiz_history=quiz_history).select_related("question")

    # Build a data structure with question, options, user's answer, and correct answer
    reviewed_questions = []
    for ua in user_answers:
        q = ua.question
        correct_answers = q.get_correct_answers()

        reviewed_questions.append({
            "question": q,
            "options": q.get_options(),  # you must have a method for choices (A, B, C, D)
            "user_answers": ua.selected_answers,
            "correct_answers": correct_answers,
            "is_correct": ua.is_correct,
        })

    context = {
        "quiz_history": quiz_history,
        "reviewed_questions": reviewed_questions,
    }
    return render(request, "quiz/quiz_review.html", context)

class GenerateQuizView(LoginRequiredMixin, View):
    """
    AJAX view to generate AI-powered quizzes
    """
    
    def post(self, request):
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            category_id = data.get('category_id')
            subcategory_id = data.get('subcategory_id')
            difficulty = data.get('difficulty', 'M')
            num_questions = data.get('num_questions', 10)
            
            # Validate required fields
            if not category_id or not subcategory_id:
                return JsonResponse({
                    'error': 'Category and subcategory are required'
                }, status=400)
            
            # Validate difficulty
            if difficulty not in ['E', 'M', 'H']:
                difficulty = 'M'  # Default to medium
            
            # Validate number of questions
            try:
                num_questions = int(num_questions)
                if num_questions < 1 or num_questions > 50:
                    num_questions = 10  # Default to 10
            except (ValueError, TypeError):
                num_questions = 10
            
            # Get category and subcategory objects
            category = get_object_or_404(Category, id=category_id)
            subcategory = get_object_or_404(SubCategory, id=subcategory_id)
            
            # TODO: Replace this with your actual AI generation function
            # For now, I'll create a placeholder that you can replace
            
            # ✅ Uncomment this line when you have the helper function:
            # questions_data = generate_quiz_questions(
            #     category.name,
            #     subcategory.name,
            #     difficulty,
            #     num_questions,
            #     request.user
            # )
            
            # 🔄 TEMPORARY: Mock data generator (replace with your AI function)
            questions_data = self.generate_mock_questions(
                category.name, 
                subcategory.name, 
                difficulty, 
                num_questions
            )
            
            if not questions_data:
                return JsonResponse({
                    'error': 'Failed to generate questions'
                }, status=500)
            
            # Create the quiz
            quiz = Quiz.objects.create(
                title=f"AI Generated Quiz - {subcategory.name}",
                description=f"Automatically generated quiz about {subcategory.name}",
                category=category,
                subcategory=subcategory,
                difficulty=difficulty,
                is_ai_generated=True,
                time_limit_minutes=num_questions * 2  # 2 minutes per question
            )
            
            print(f"=== SAVING {len(questions_data)} QUESTIONS TO DATABASE ===")
            
            # Create questions
            for i, q_data in enumerate(questions_data):
                print(f"Processing question {i+1}:")
                print(f"  Text: {q_data['text']}")
                print(f"  Option1: '{q_data.get('option1', '')}'")
                print(f"  Option2: '{q_data.get('option2', '')}'")
                print(f"  Option3: '{q_data.get('option3', '')}'")
                print(f"  Option4: '{q_data.get('option4', '')}'")
                print(f"  Correct Answer: '{q_data.get('correct_answer', '')}'")
                
                # Validate options
                if not all([
                    q_data.get('option1'), 
                    q_data.get('option2'), 
                    q_data.get('option3'), 
                    q_data.get('option4')
                ]):
                    print(f"  WARNING: Some options are empty for question {i+1}")
                
                # Create question
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['text'],
                    option1=q_data.get('option1', ''),
                    option2=q_data.get('option2', ''),
                    option3=q_data.get('option3', ''),
                    option4=q_data.get('option4', ''),
                    correct_answer=q_data.get('correct_answer', 'A'),
                    difficulty=difficulty,
                    is_ai_generated=True
                )
                
                print(f"  Saved with ID {question.id}")
                print("-----")
            
            return JsonResponse({
                'success': True,
                'quiz_id': quiz.id,
                'message': f'Generated {len(questions_data)} questions',
                'redirect_url': f'/quiz/take/{quiz.id}/'  # Optional: provide redirect URL
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
            
        except Category.DoesNotExist:
            return JsonResponse({
                'error': 'Category not found'
            }, status=404)
            
        except SubCategory.DoesNotExist:
            return JsonResponse({
                'error': 'Subcategory not found'
            }, status=404)
            
        except Exception as e:
            print(f"ERROR in GenerateQuizView: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': f'An error occurred: {str(e)}'
            }, status=500)
    
    def generate_mock_questions(self, category_name, subcategory_name, difficulty, num_questions):
        """
        🔄 TEMPORARY: Mock question generator
        Replace this with your actual AI generation function
        """
        questions = []
        
        difficulty_text = {
            'E': 'Easy',
            'M': 'Medium', 
            'H': 'Hard'
        }.get(difficulty, 'Medium')
        
        for i in range(num_questions):
            question_data = {
                'text': f"Sample {difficulty_text} question {i+1} about {subcategory_name} in {category_name}?",
                'option1': f"Option A for question {i+1}",
                'option2': f"Option B for question {i+1}",
                'option3': f"Option C for question {i+1}",
                'option4': f"Option D for question {i+1}",
                'correct_answer': ['A', 'B', 'C', 'D'][i % 4]  # Rotate correct answers
            }
            questions.append(question_data)
        
        return questions
    
    def get(self, request):
        """Handle GET requests (not allowed for this endpoint)"""
        return JsonResponse({
            'error': 'GET method not allowed. Use POST to generate quizzes.'
        }, status=405)
    
def take_quiz(request, quiz_id):
    """
    Display quiz taking interface
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by('id')  # Get all questions for this quiz
    
    if not questions.exists():
        messages.error(request, 'This quiz has no questions.')
        return redirect('quiz_list')
    
    # Create a quiz history record to track this attempt
    if request.user.is_authenticated:
        # You might want to create a QuizHistory model to track attempts
        # For now, we'll just pass the quiz_id
        quiz_history_id = f"temp_{quiz_id}_{request.user.id}"
    else:
        quiz_history_id = f"temp_{quiz_id}_anonymous"
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'quiz_history_id': quiz_history_id,
    }
    
    return render(request, 'quizzes/take_quiz.html', context)


@login_required
def submit_quiz(request):
    """
    Handle quiz submission and calculate results
    """
    if request.method == 'POST':
        try:
            quiz_history_id = request.POST.get('quiz_history_id')
            answers_json = request.POST.get('answers')
            time_taken = request.POST.get('time_taken', 0)
            
            if not answers_json:
                messages.error(request, 'No answers received.')
                return redirect('quiz_list')
            
            # Parse answers
            try:
                answers = json.loads(answers_json)
            except json.JSONDecodeError:
                messages.error(request, 'Invalid answer format.')
                return redirect('quiz_list')
            
            # Calculate score
            total_questions = 0
            correct_answers = 0
            quiz = None
            question_results = {}
            
            for question_id, answer_data in answers.items():
                try:
                    question = Question.objects.get(id=int(question_id))
                    if not quiz:
                        quiz = question.quiz
                    
                    total_questions += 1
                    selected_option = answer_data.get('selected_option', '')
                    is_correct = selected_option == question.correct_answer
                    
                    if is_correct:
                        correct_answers += 1
                    
                    question_results[question_id] = {
                        'question': question,
                        'selected_option': selected_option,
                        'correct_answer': question.correct_answer,
                        'is_correct': is_correct
                    }
                    
                except (Question.DoesNotExist, ValueError):
                    continue
            
            # Calculate percentage
            if total_questions > 0:
                score_percentage = round((correct_answers / total_questions) * 100, 2)
            else:
                score_percentage = 0
            
            # Store results in session for display
            request.session['quiz_results'] = {
                'quiz_id': quiz.id if quiz else None,
                'quiz_title': quiz.title if quiz else 'Unknown Quiz',
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'score_percentage': score_percentage,
                'time_taken': time_taken,
                'question_results': {
                    qid: {
                        'question_text': result['question'].text,
                        'selected_option': result['selected_option'],
                        'correct_answer': result['correct_answer'],
                        'is_correct': result['is_correct'],
                        'options': {
                            'A': result['question'].option1,
                            'B': result['question'].option2,
                            'C': result['question'].option3,
                            'D': result['question'].option4,
                        }
                    } for qid, result in question_results.items()
                }
            }
            
            return redirect('quiz_results')
            
        except Exception as e:
            print(f"Error in submit_quiz: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, 'An error occurred while processing your quiz.')
            return redirect('quiz_list')
    
    return redirect('quiz_list')


def quiz_results(request):
    """
    Display quiz results
    """
    results = request.session.get('quiz_results')
    
    if not results:
        messages.error(request, 'No quiz results found.')
        return redirect('quiz_list')
    
    # Clear results from session after displaying
    if 'quiz_results' in request.session:
        del request.session['quiz_results']
    
    return render(request, 'quizzes/quiz_results.html', {'results': results})


def quiz_detail(request, quiz_id):
    """
    Display quiz details (for editing/viewing)
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by('id')
    
    # Check if user has permission to view/edit
    if not request.user.is_staff and quiz.category.created_by != request.user:
        messages.error(request, 'You do not have permission to view this quiz.')
        return redirect('quiz_list')
    
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    
    return render(request, 'quizzes/quiz_detail.html', context)


# Optional: API endpoint to get quiz data as JSON
def quiz_api(request, quiz_id):
    """
    Return quiz data as JSON (for AJAX requests)
    """
    try:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions = quiz.questions.all().order_by('id')
        
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'category': quiz.category.name,
            'subcategory': quiz.subcategory.name if quiz.subcategory else None,
            'difficulty': quiz.get_difficulty_display(),
            'time_limit_minutes': quiz.time_limit_minutes,
            'questions': []
        }
        
        for question in questions:
            quiz_data['questions'].append({
                'id': question.id,
                'text': question.text,
                'options': {
                    'A': question.option1,
                    'B': question.option2,
                    'C': question.option3,
                    'D': question.option4,
                }
                # Don't include correct_answer in API response for security
            })
        
        return JsonResponse(quiz_data)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)