# importing necessary libraries

from flask import Blueprint, request, session, jsonify
from app.extensions import db, cache
from app.models.models import Role, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
from flask_security import roles_required, hash_password
from flask_login import current_user
from app.data_access import get_dashboard_data
# @roles_required gives 403 Forbidden and @auth_required gives 401 Unauthorized

# creating blueprint: to organize a Flask application into reusable, maintainable units, 
#                     encapsulating views, templates, and static files, 
#                     which are then registered with the main application app.py

admin_controller = Blueprint('admin_controller', __name__, url_prefix = '/api/admin')

# utility function
def error(message, status_code = 400):
    return jsonify({'error': message}), status_code

# dashboard

@admin_controller.route('/dashboard', methods = ['GET', 'POST'])
@roles_required('admin')
def dashboard():
    
    if request.method == 'GET':
        # does it cause more load to read all subjects in this url? try reading about pagination or lazy loading?
        subjects = Subject.query.all()
        subject_data = []
        for subject in subjects:
            chapters = Chapter.query.filter_by(subject_id = subject.id).all()
            chapter_list = []
            for chapter in chapters:
                quizzes = Quiz.query.filter_by(chapter_id = chapter.id).all()
                quiz_list = []
                for quiz in quizzes:
                    questions = Question.query.filter_by(quiz_id = quiz.id).all()
                    quiz_list.append({
                        'id': quiz.id,
                        'name': quiz.name, 
                        'description': quiz.description,
                        'questions': [{
                                'id': q.id, 
                                'text': q.question_text, 
                                'option1': q.option1, 
                                'option2': q.option2, 
                                'option3': q.option3, 
                                'option4': q.option4, 
                                'correct_option': q.correct_option 
                            } for q in questions
                    ]})
                chapter_list.append({
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'quizzes': quiz_list
                })
            subject_data.append({
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'chapters': chapter_list
            })
        users = User.query.all()
        return jsonify({'subject_data': subject_data, 'user_data': [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]}), 200
    
    # search functionality
    if request.method == 'POST':
        
        data = request.get_json()
        query = data.get('query')
        
        user_data = []
        users = User.query.filter(User.username.like(f'%{query}%')).all()
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        
        subject_data = []

        subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
        chapters = Chapter.query.filter(Chapter.name.ilike(f'%{query}%')).all()
        quizzes = Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all()
        questions = Question.query.filter(Question.question_text.ilike(f'%{query}%')).all()

        def add_to_subject_data(subject, chapter = None, quiz = None, question = None):
            
            sub = next((s for s in subject_data if s['id'] == subject.id), None)
            if not sub:
                sub = {
                    'id': subject.id,
                    'name': subject.name,
                    'description': subject.description,
                    'chapters': []
                }
                subject_data.append(sub)

            if chapter:
                ch = next((c for c in sub['chapters'] if c['id'] == chapter.id), None)
                if not ch:
                    ch = {
                        'id': chapter.id,
                        'name': chapter.name,
                        'description': chapter.description,
                        'quizzes': []
                    }
                    sub['chapters'].append(ch)
                if quiz:
                    qz = next((q for q in ch['quizzes'] if q['id'] == quiz.id), None)
                    if not qz:
                        qz = {
                            'id': quiz.id,
                            'name': quiz.name,
                            'description': quiz.description,
                            'questions': []
                        }
                        ch['quizzes'].append(qz)
                    if question:
                        if not any(q['id'] == question.id for q in qz['questions']):
                            qz['questions'].append({
                                'id': question.id,
                                'text': question.question_text,
                                'option1': question.option1,
                                'option2': question.option2,
                                'option3': question.option3,
                                'option4': question.option4,
                                'correct_option': question.correct_option
                            })

        # subjects matched by name
        for subject in subjects:
            chapters_ = Chapter.query.filter_by(subject_id = subject.id).all()
            for chapter in chapters_:
                quizzes_ = Quiz.query.filter_by(chapter_id = chapter.id).all()
                for quiz in quizzes_:
                    questions_ = Question.query.filter_by(quiz_id = quiz.id).all()
                    for question in questions_:
                        add_to_subject_data(subject, chapter, quiz, question)
                    if not questions_:
                        add_to_subject_data(subject, chapter, quiz)
                if not quizzes_:
                    add_to_subject_data(subject, chapter)
            if not chapters_:
                add_to_subject_data(subject)

        # chapters matched by name
        for chapter in chapters:
            subject = Subject.query.get(chapter.subject_id)
            quizzes_ = Quiz.query.filter_by(chapter_id = chapter.id).all()
            for quiz in quizzes_:
                questions_ = Question.query.filter_by(quiz_id = quiz.id).all()
                for question in questions_:
                    add_to_subject_data(subject, chapter, quiz, question)
                if not questions_:
                    add_to_subject_data(subject, chapter, quiz)
            if not quizzes_:
                add_to_subject_data(subject, chapter)

        # quizzes matched by name
        for quiz in quizzes:
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            questions_ = Question.query.filter_by(quiz_id = quiz.id).all()
            for question in questions_:
                add_to_subject_data(subject, chapter, quiz, question)
            if not questions_:
                add_to_subject_data(subject, chapter, quiz)

        # questions matched by text
        for question in questions:
            quiz = Quiz.query.get(question.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            add_to_subject_data(subject, chapter, quiz, question)

        return jsonify({'subject_data': subject_data, 'user_data': user_data}), 200
        

# users: functions explain their utility by their name

# how to mimic flask_security mechanisms of registration for the admin?

@admin_controller.route('/user/create', methods = ['POST'])
@roles_required('admin')
def create_user():
    
    data = request.get_json()
    required = ['username', 'password', 'email']
    if not all(k in data for k in required):
        return error('missing parameters', 400)
    if User.query.filter_by(username = data.get('username')).first():
        return error('username already exists', 400)
    if User.query.filter_by(email = data.get('email')).first():
        return error('email already exists', 400)
    
    # register_user() ensures all signals, emails, and custom logic are triggered, just as with regular user registration.

    user = User(
        username = data.get('username'),
        password = hash_password(data.get('password')),
        email = data.get('email'),
        roles = [Role.query.filter_by(name = 'user').first()],
        active = True
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created', 'id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return error(e, 500) 

@admin_controller.route('/user/delete/<int:user_id>', methods = ['DELETE'])
@roles_required('admin')
def delete_user(user_id):
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return error('user not found', 404)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'user deleted'}), 200
    
    except Exception as e:
        return error(e, 500)

# subjects: functions explain their utility by the name

@admin_controller.route('/subject/create', methods = ['POST'])
@roles_required('admin')
def create_subject():
    
    data = request.get_json()
    required = ['name', 'description']
    
    if not all(k in data for k in required):
        return error('missing parameters', 400)
    
    try:
        
        subject = Subject(
            name = data.get('name'), 
            description = data.get('description')
        )
        
        db.session.add(subject)
        db.session.commit()
        
        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'subject created', 'name': subject.name}), 201
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/subject/update/<int:subject_id>', methods = ['PUT'])
@roles_required('admin')
def update_subject(subject_id):
    
    try:
        
        subject = Subject.query.get(subject_id)
        
        if not subject:
            return error('subject not found', 404)
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if name:
            subject.name = name
        if description:
            subject.description = description
        
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'subject updated'}), 200
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/subject/delete/<int:subject_id>', methods = ['DELETE'])
@roles_required('admin')
def delete_subject(subject_id):
    
    try:
        
        subject = Subject.query.get(subject_id)
        if not subject:
            return error('subject not found', 404)
        
        db.session.delete(subject)
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'subject deleted'}), 200
    
    except Exception as e:
        return error(e, 500)

# chapters: functions explain their utility by the name

@admin_controller.route('/chapter/create', methods = ['POST'])
@roles_required('admin')
def create_chapter():
    
    data = request.get_json()
    required = ['name', 'description', 'subject_id']
    if not all(k in data for k in required):
        return error('missing parameters', 400)
    if not Subject.query.get(data.get('subject_id')):
        return error('invalid subject_id', 400)
    
    try:
        chapter = Chapter(
            name = data.get('name'), 
            description = data.get('description'), 
            subject_id = data.get('subject_id')
        )

        db.session.add(chapter)
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)
        
        return jsonify({'message': 'chapter created', 'name': chapter.name}), 201
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/chapter/update/<int:chapter_id>', methods = ['PUT'])
@roles_required('admin')
def update_chapter(chapter_id):
    
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return error('chapter not found', 404)
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if name:
            chapter.name = name
        if description:
            chapter.description = description
        
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'chapter updated'}), 200
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/chapter/delete/<int:chapter_id>', methods = ['DELETE'])
@roles_required('admin')
def delete_chapter(chapter_id):
    
    try:
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return error('chapter not found', 404)
        
        db.session.delete(chapter)
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'chapter deleted'}), 200
    
    except Exception as e:
        return error(e, 500)
    
# quizzes: functions explain their utility by the name

@admin_controller.route('/quiz/create', methods = ['POST'])
@roles_required('admin')
def create_quiz():

    data = request.get_json()
    required = ['name', 'description', 'chapter_id', 'date_of_quiz', 'time_duration']
    
    if not all(k in data for k in required):
        return error('missing parameters', 400)
    
    try: 
        date_of_quiz = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%dT%H:%M')
        time_duration = datetime.strptime(data.get('time_duration'), '%H:%M').time()
    
    except Exception as e:
        return error(e, 500)

    if not Chapter.query.get(data.get('chapter_id')):
        return error('invalid chapter_id', 400)
    
    try:
        
        quiz = Quiz(
            name = data.get('name'), 
            description = data.get('description'), 
            chapter_id = data.get('chapter_id'), 
            date_of_quiz = date_of_quiz, 
            time_duration = time_duration
        )

        db.session.add(quiz)
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'quiz created', 'name': quiz.name}), 201
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/quiz/update/<int:quiz_id>', methods = ['PUT'])
@roles_required('admin')
def update_quiz(quiz_id):
    
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return error('quiz not found', 404)
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        chapter_id = data.get('chapter_id')
        date_of_quiz = data.get('date_of_quiz')
        time_duration = data.get('time_duration')
        if name:
            quiz.name = name
        if description:
            quiz.description = description
        if chapter_id:
            quiz.chapter_id = chapter_id
        if date_of_quiz:
            try:
                quiz.date_of_quiz = datetime.strptime(date_of_quiz, '%Y-%m-%dT%H:%M')
            except Exception as e:
                return error(e, 500)
        if time_duration:
            try:
                quiz.time_duration = datetime.strptime(time_duration, '%H:%M').time()
            except Exception as e:
                return error(e, 500)
        
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'quiz updated'}), 200
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/quiz/delete/<int:quiz_id>', methods = ['DELETE'])
@roles_required('admin')
def delete_quiz(quiz_id):
    
    try:
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return error('quiz not found', 404)
        
        db.session.delete(quiz)
        db.session.commit()

        users = User.query.all()
        for user in users:
            cache.delete_memoized(get_dashboard_data, user.id)

        return jsonify({'message': 'quiz deleted'}), 200
    
    except Exception as e:
        return error(e, 500)

# questions: functions explain their utility by the name

@admin_controller.route('/question/create/<int:quiz_id>', methods = ['POST'])
@roles_required('admin')
def create_question(quiz_id):
    
    data = request.get_json()
    required = ['question_text', 'option1', 'option2', 'option3', 'option4', 'correct_option']
    if not all(k in data for k in required):
        return error('missing parameters', 400)
    if not Quiz.query.get(quiz_id):
        return error('invalid quiz_id', 404)
    
    try:
        
        question = Question(
            quiz_id = quiz_id, 
            question_text = data.get('question_text'), 
            option1 = data.get('option1'), 
            option2 = data.get('option2'), 
            option3 = data.get('option3'), 
            option4 = data.get('option4'), 
            correct_option = data.get('correct_option')
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({'message': 'question created', 'name': question.question_text}), 201
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/question/update/<int:question_id>', methods = ['PUT'])
@roles_required('admin')
def update_question(question_id):
    
    try:
        question = Question.query.get(question_id)
        if not question:
            return error('question not found', 404)
        
        data = request.get_json()
        question_text = data.get('question_text')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        correct_option = data.get('correct_option')
        if question_text:
            question.question_text = question_text
        if option1:
            question.option1 = option1
        if option2:
            question.option2 = option2
        if option3:
            question.option3 = option3
        if option4:
            question.option4 = option4
        if correct_option:
            question.correct_option = correct_option
        
        db.session.commit()
        
        return jsonify({'message': 'quiz updated'}), 200
    
    except Exception as e:
        return error(e, 500)

@admin_controller.route('/question/delete/<int:question_id>', methods = ['DELETE'])
@roles_required('admin')
def delete_question(question_id):
    
    try:
        
        question = Question.query.get(question_id)
        if not question:
            return error('question not found', 404)
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({'message': 'question deleted'}), 200
    
    except Exception as e:
        return error(e, 500)

# summary tables

@admin_controller.route('/summary', methods = ['GET'])
@roles_required('admin')
def summary():
    
    subjects = Subject.query.all()
    subject_data = []
    
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id = subject.id).all()
        chapter_data = []
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id = chapter.id).all()
            quiz_data = []
            for quiz in quizzes:
                question_count = Question.query.filter_by(quiz_id = quiz.id).count()
                scores = Score.query.filter_by(quiz_id = quiz.id).all()
                if scores:
                    user_attempts = {}
                    for score in scores:
                        user_attempts[score.user_id] = score
                    average_score = sum(score.total_score for score in user_attempts.values()) / len(user_attempts)
                    attempts = len(scores)
                else:
                    average_score = 0
                    attempts = 0
                quiz_data.append({
                    'name': quiz.name, 
                    'description': quiz.description, 
                    'question_count': question_count, 
                    'average_score': round(average_score, 2), 
                    'attempts': attempts
                })
            
            chapter_data.append({
                'name': chapter.name, 
                'description': chapter.description,
                'quiz_data': quiz_data
            })
        
        subject_data.append({
            'name': subject.name, 
            'description': subject.description, 
            'chapters': chapter_data
        })
    
    users = User.query.join(User.roles).filter(Role.name == 'user').all()
    user_data = []
    for user in users:
        scores = Score.query.filter_by(user_id = user.id).all()
        if scores:
            user_quizzes = {}
            for score in scores:
                user_quizzes[score.quiz_id] = score
            subject_scores = {}
            for quiz_id, score in user_quizzes.items():
                quiz = Quiz.query.get(quiz_id)
                chapter = Chapter.query.get(quiz.chapter_id)
                subject = Subject.query.get(chapter.subject_id)
                if subject.id not in subject_scores:
                    subject_scores[subject.id] = {'subject': subject, 'scores': [], 'attempts': 0}
                subject_scores[subject.id]['scores'].append(score.total_score)
                subject_scores[subject.id]['attempts'] += Score.query.filter_by(user_id = user.id, quiz_id = quiz_id).count()
            subject_info = []
            for subject_id, data in subject_scores.items():
                avg_score = sum(data['scores']) / len(data['scores'])
                subject_info.append({
                    'name': data['subject'].name, 'average_score': round(avg_score, 2), 'attempts': data['attempts']})
        else:
            subject_info = []
        user_data.append({'user': [{'username': user.username, 'email': user.email}], 'subjects': subject_info})

    return jsonify({'subject_data': subject_data, 'user_data': user_data})
