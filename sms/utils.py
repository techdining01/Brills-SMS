import random
from django.db import transaction
from .models import Question, Exam

def generate_randomized_session_data(session: Exam):
    """
    Generates the randomized question and option order for a new CBT session.
    
    Returns:
        A dictionary suitable for saving to Exam.question_order_data
    """
    
    # 1. Fetch all questions for the student's subject
    questions = list(Question.objects.filter(subject=session.subject))
    
    # Ensure there are questions to prevent errors
    if not questions:
        raise ValueError("No questions found for this subject.")

    # 2. Randomly shuffle the order of the questions themselves
    random.shuffle(questions)
    
    # 3. Create the data structure for the JSONField
    session_data = {
        'questions': [],
        'student_answers': {},
    }
    
    # 4. Iterate through questions and randomize options
    options_indices = [0, 1, 2, 3] # Represents original A, B, C, D positions

    for i, question in enumerate(questions):
        # Create a unique shuffle of the indices for THIS specific question
        randomized_indices = random.sample(options_indices, len(options_indices))
        
        # Determine the NEW position of the correct answer
        original_correct_index = question.is_correct  # e.g., 0 for A, 1 for B, etc.
        
        # Find where the original correct index moved to in the randomized list
        new_correct_position = randomized_indices.index(original_correct_index)
        
        # Build the question entry for the session
        session_data['questions'].append({
            'question_id': question.id,
            # This is the core data: a map from the new option position 
            # (0, 1, 2, 3 on the student's screen) to the original option index.
            'option_map': randomized_indices,
            # The correct answer in the student's NEW option position (e.g., if A=0 
            # moved to the 3rd spot, the new_correct_position is 3).
            'correct_position': new_correct_position, 
        })
        
    return session_data

@transaction.atomic
def start_cbt_session(student, subject):
    """
    Creates and initializes a new CBT exam session.
    """
    # Create the session object first
    session = Exam.objects.create(
        student=student,
        subject=subject,
    )
    
    # Generate the randomized data
    data = generate_randomized_session_data(session)
    
    # Save the complex data to the session
    session.question_order_data = data
    session.save()
    
    return session


# sms/utils.py
import json
import random

# Mock data generation function (to be replaced by real calculation later)
def get_student_performance_data(student_id):
    """
    Generates structured mock data suitable for Chart.js visualization.
    In a real app, this would query CBTExamSession results.
    """
    # Mock subjects and scores
    subjects = ['Mathematics', 'English', 'Science', 'History', 'Art']
    
    # 1. Subject Performance Data (e.g., Radar Chart Data)
    subject_scores = [random.randint(50, 95) for _ in subjects]
    
    # 2. Score History Data (e.g., Line Chart Data)
    exam_dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    history_scores = [random.randint(60, 90) for _ in exam_dates]
    
    return {
        'subject_labels': json.dumps(subjects),
        'subject_scores': json.dumps(subject_scores),
        'history_labels': json.dumps(exam_dates),
        'history_scores': json.dumps(history_scores),
    }

# We'll keep the start_cbt_session function here when you decide to clean up.
# def start_cbt_session(...)
# ...