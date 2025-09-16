import google.generativeai as genai
from django.conf import settings
import re

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

class AIQuizGenerator:
    @staticmethod
    def generate_quiz(category, subcategory, difficulty, num_questions, user,topic= None):
        try:
            prompt = (
                f"Generate {num_questions} multiple-choice quiz questions for category '{category}' "
                f"and subcategory '{subcategory}' at difficulty level '{difficulty}'. "
                "Each question should have 4 options (A, B, C, D) and specify the correct answer."
                "Please format them as:\n"
                "Q1: Question text\n"
                "A) option1\nB) option2\nC) option3\nD) option4\nAnswer: X\n\n"
            )

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            questions = []
            if response and response.text:
                blocks = response.text.strip().split("\n\n")
                for block in blocks:
                    lines = [line.strip() for line in block.splitlines() if line.strip()]
                    if len(lines) >= 5:
                        # Extract question text
                        q_text = re.sub(r'^Q\d+:', '', lines[0]).strip()

                        # Extract options
                        opts = {}
                        for line in lines[1:5]:
                            match = re.match(r'^[A-D][\).\s]+(.+)', line)
                            if match:
                                key = line[0]  # A/B/C/D
                                opts[key] = match.group(1).strip()
                            else:
                                opts[line[0]] = line.split(" ", 1)[1].strip()

                        # Extract correct answer
                        answer_line = next((l for l in lines if "Answer:" in l), "")
                        correct = answer_line.replace("Answer:", "").strip()

                        # Ensure all options exist
                        for k in "ABCD":
                            opts.setdefault(k, "")

                        questions.append({
                            "text": q_text,
                            "option1": opts["A"],
                            "option2": opts["B"],
                            "option3": opts["C"],
                            "option4": opts["D"],
                            "correct_answer": correct
                        })

            print(f"DEBUG: Parsed {len(questions)} questions ✅")
            return questions

        except Exception as e:
            print("Error in generate_quiz_questions:", e)
            import traceback
            traceback.print_exc()
            return []
