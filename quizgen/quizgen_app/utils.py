import openai
import json
import random
from django.conf import settings
from .models import Category, SubCategory, Quiz, Question

# AI Quiz Generation Service
class AIQuizGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_quiz(self, category_name, subcategory_name=None, difficulty='easy', questions_count=5):
        """Generate quiz questions using OpenAI API"""
        
        topic = f"{category_name}"
        if subcategory_name:
            topic += f" - {subcategory_name}"

        prompt = f"""
        Generate {questions_count} multiple choice questions about {topic} at {difficulty} difficulty level.
        
        Format each question as JSON with this structure:
        {{
            "question": "Question text here?",
            "options": {{
                "A": "Option A text",
                "B": "Option B text", 
                "C": "Option C text",
                "D": "Option D text"
            }},
            "correct_answer": "A",
            "explanation": "Brief explanation of why this is correct"
        }}
        
        Return only a JSON array of {questions_count} questions. Make sure questions are relevant to {topic} and appropriate for {difficulty} level.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert quiz creator. Generate high-quality, educational multiple choice questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
                
            questions_data = json.loads(content)
            return questions_data
            
        except Exception as e:
            # Fallback to sample questions if API fails
            return self.get_fallback_questions(category_name, difficulty, questions_count)

    def get_fallback_questions(self, category_name, difficulty, questions_count):
        """Fallback questions when AI generation fails"""
        
        fallback_questions = {
            'DSA': [
                {
                    "question": "What is the time complexity of binary search?",
                    "options": {
                        "A": "O(n)",
                        "B": "O(log n)",
                        "C": "O(n log n)",
                        "D": "O(n²)"
                    },
                    "correct_answer": "B",
                    "explanation": "Binary search divides the search space in half with each comparison."
                },
                {
                    "question": "Which data structure follows LIFO principle?",
                    "options": {
                        "A": "Queue",
                        "B": "Stack",
                        "C": "Array",
                        "D": "Linked List"
                    },
                    "correct_answer": "B",
                    "explanation": "Stack follows Last In First Out (LIFO) principle."
                }
            ],
            'Programming Language': [
                {
                    "question": "Which of the following is not a programming language?",
                    "options": {
                        "A": "Python",
                        "B": "Java",
                        "C": "HTML",
                        "D": "C++"
                    },
                    "correct_answer": "C",
                    "explanation": "HTML is a markup language, not a programming language."
                }
            ],
            'Mathematics': [
                {
                    "question": "What is the derivative of x²?",
                    "options": {
                        "A": "x",
                        "B": "2x",
                        "C": "x²",
                        "D": "2"
                    },
                    "correct_answer": "B",
                    "explanation": "Using the power rule: d/dx(x²) = 2x"
                }
            ],
            'Physics': [
                {
                    "question": "What is the unit of force?",
                    "options": {
                        "A": "Joule",
                        "B": "Watt",
                        "C": "Newton",
                        "D": "Pascal"
                    },
                    "correct_answer": "C",
                    "explanation": "Newton (N) is the SI unit of force."
                }
            ]
        }
        
        # Get available questions for the category
        available_questions = fallback_questions.get(category_name, fallback_questions['DSA'])
        
        # Return requested number of questions (repeat if necessary)
        questions = []
        for i in range(questions_count):
            questions.append(available_questions[i % len(available_questions)])
            
        return questions

    def create_quiz_from_ai(self, user, category, subcategory, difficulty, questions_count, time_limit):
        """Create a complete quiz with AI-generated questions"""
        
        # Generate quiz title
        title_parts = [category.name]
        if subcategory:
            title_parts.append(subcategory.name)
        title_parts.extend([difficulty.title(), "Quiz"])
        
        quiz_title = " - ".join(title_parts)
        
        # Create quiz object
        quiz = Quiz.objects.create(
            title=quiz_title,
            category=category,
            subcategory=subcategory,
            difficulty=difficulty,
            questions_count=questions_count,
            time_limit=time_limit,
            created_by=user,
            is_ai_generated=True
        )
        
        # Generate questions using AI
        subcategory_name = subcategory.name if subcategory else None
        questions_data = self.generate_quiz(
            category.name,
            subcategory_name,
            difficulty,
            questions_count
        )
        
        # Create question objects
        for q_data in questions_data:
            Question.objects.create(
                quiz=quiz,
                text=q_data['question'],
                option_a=q_data['options']['A'],
                option_b=q_data['options']['B'],
                option_c=q_data['options']['C'],
                option_d=q_data['options']['D'],
                correct_answer=q_data['correct_answer'],
                explanation=q_data.get('explanation', '')
            )
        
        return quiz

def get_leaderboard(limit=10):
    """Get top users by average score"""
    from .models import UserProfile
    from django.contrib.auth.models import User
    
    # Update all user profiles
    for user in User.objects.all():
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.update_stats()
    
    return UserProfile.objects.filter(total_quizzes__gt=0).order_by('-average_score')[:limit]