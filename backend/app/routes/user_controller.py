# importing necessary libraries

from flask import Blueprint, request, session, jsonify
from app.extensions import db, cache
from app.models.models import User, Subject, Chapter, Quiz, Question, Score, Response
from datetime import datetime, timedelta
from flask_security import roles_required
from flask_login import current_user
from app.data_access import get_dashboard_data, get_search_results

from app import tasks

# creating blueprint: to organize a Flask application into reusable, maintainable units, 
#                     encapsulating views, templates, and static files, 
#                     which are then registered with the main application app.py

user_controller = Blueprint('user_controller', __name__, url_prefix = '/api/user')

# utility function
def error(message, status_code = 400):
    return jsonify({'error': message}), status_code

# dashboard

@user_controller.route('/dashboard', methods = ['GET', 'POST'])
@roles_required('user')
def dashboard():
    if request.method == 'GET':
        # does it cause more load to read all subjects in this url? try reading about pagination or lazy loading?
        subject_data = get_dashboard_data(current_user.id)
        return jsonify({'subject_data': subject_data}), 200
    
    # search functionality
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
        subject_data = get_search_results(current_user.id, query)
        return jsonify({'subject_data': subject_data}), 200

@user_controller.route('/quiz/<int:quiz_id>/start', methods = ['GET'])
@roles_required('user')
def start_quiz(quiz_id):

    # sends quiz questions to the frontend

    try:
        
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return error('quiz not found', 404)
        
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        
        time_now = datetime.now() + timedelta(hours = 5, minutes = 30)
        quiz_duration = quiz.time_duration.hour * 3600 + quiz.time_duration.minute * 60
        
        if time_now >= quiz.date_of_quiz:

            # allows to attempt quiz only after the time entered by the admin

            questions = Question.query.filter_by(quiz_id = quiz_id).all()
            
            subject_data = {
                'name': subject.name, 
                'chapter': {
                    'id': chapter.id, 
                    'name': chapter.name, 
                    'quiz': {
                        'id': quiz.id, 
                        'name': quiz.name,
                        'time_duration': quiz_duration,
                        'questions': [{
                            'id': q.id,
                            'text': q.question_text,
                            'option1': q.option1,
                            'option2': q.option2,
                            'option3': q.option3,
                            'option4': q.option4,
                        } for q in questions]
                    }
                }
            }

            return jsonify({'subject_data': subject_data}), 200

        else:
            return error('this quiz can not be started now', 503)
    
    except Exception as e:
        return error(e, 500)

@user_controller.route('/quiz/<int:quiz_id>/end', methods = ['POST'])
@roles_required('user')
def end_quiz(quiz_id):

    # accepts responses from the user and stores in the database 
        
    quiz = Quiz.query.get(quiz_id)
    
    if not quiz:
        return error('quiz not found', 404)
    
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    
    questions = Question.query.filter_by(quiz_id = quiz_id).all()
    
    data = request.get_json()
    
    total_questions = len(questions)
    correct_questions = 0
    
    flag = False
    
    for question in questions:

        marked = 0
        
        user_option = data.get(f'{question.id}')
        if user_option:
            if int(user_option) == question.correct_option:
                correct_questions += 1
                flag = True
                marked = int(user_option)
            else:
                flag = False
                marked = int(user_option)
        else:
            flag = False
            marked = 0
        
        try:
            # response model stores only one attempt of the question 
            response = Response.query.filter_by(user_id = current_user.id, question_id = question.id).first()
            
            if not response:
                response = Response(
                    user_id = current_user.id,
                    question_id = question.id,
                    marked = marked,
                    correct = flag
                )
                db.session.add(response)
                db.session.commit()
            
            else:
                return error('already attempted', 400)
            
            cache.delete_memoized(get_dashboard_data, current_user.id)
            
        except Exception as e:
            return error(e, 500)

    total_score = correct_questions / total_questions * 100
    
    try:
        score = Score(
            user_id = current_user.id, 
            quiz_id = quiz_id, 
            total_score = total_score, 
            time_of_attempt = datetime.now()
        )
        db.session.add(score)
        db.session.commit()
    
    except Exception as e:
        return error(e, 500)
    
    return jsonify({'subject': subject.name, 'chapter': chapter.name, 'quiz': quiz.name, 'score': total_score})

@user_controller.route('/quiz/<int:quiz_id>/score', methods = ['GET'])
@roles_required('user')
def score(quiz_id):

    # sends response sheet with score, user attempts, and correct answers to the user

    score = Score.query.filter_by(user_id = current_user.id, quiz_id = quiz_id).first()
    
    if not score:
        return error('score not found', 404)
    
    questions = Question.query.filter_by(quiz_id = quiz_id).all()
    responses = []
    for question in questions:
        response = Response.query.filter_by(user_id = current_user.id, question_id = question.id).first()
        responses.append({
            question.id: {
                "text": question.question_text, 
                "option1": question.option1, 
                "option2": question.option2, 
                "option3": question.option3, 
                "option4": question.option4, 
                "option_marked": response.marked, 
                "option_correct": response.correct,
                "correct_option": question.correct_option
                }
            }
        )

    quiz = Quiz.query.get(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    subject_data = {
        'subject': [subject.name, subject.description], 
        'chapter': [chapter.name, chapter.description], 
        'quiz': [quiz.name, quiz.description],
        'responses': responses,
        'score': [score.total_score]
    }
    return jsonify({'subject_data': subject_data})

# summary
@user_controller.route('/summary', methods = ['GET'])
@roles_required('user')
def summary():

    try:
        subjects = Subject.query.all()
        summary_data = []
        for subject in subjects:
            subject_dict = {'name': subject.name, 'description': subject.description, 'chapters': []}
            chapters = Chapter.query.filter_by(subject_id = subject.id).all()
            for chapter in chapters:
                chapter_dict = {'name': chapter.name,'description': chapter.description, 'quizzes': [], 'avg_score': 0}
                quizzes = Quiz.query.filter_by(chapter_id = chapter.id).all()
                for quiz in quizzes:
                    score = Score.query.filter_by(user_id = current_user.id, quiz_id = quiz.id).first()
                    if score:
                        score = score.total_score
                    else:
                        score = 0
                    quiz_dict = {'name': quiz.name, 'score': score}
                    chapter_dict['quizzes'].append(quiz_dict)
                subject_dict['chapters'].append(chapter_dict)
            summary_data.append(subject_dict)
    
    except Exception as e:
        return error(e, 500)

    return jsonify({'summary_data': summary_data})


@user_controller.route('/export', methods = ['GET'])
@roles_required('user')
def export_quiz_data():
    
    # enqueue the celery task
    job = tasks.export_user_quiz_data.delay(current_user.id)

    return jsonify({'status': 'task started'}), 202