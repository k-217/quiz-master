from app.models.models import Subject, Chapter, Quiz, Question, Response
from app.extensions import cache

@cache.memoize(timeout=300)
def get_dashboard_data(user_id):
    subjects = Subject.query.all()
    subject_data = []
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id = subject.id).all()
        chapter_list = []
        for chapter in chapters:
            quizzes = Quiz.query.filter_by(chapter_id = chapter.id).all()
            quiz_list = []
            for quiz in quizzes:
                attempted = False

                questions = Question.query.filter_by(quiz_id = quiz.id).all()

                for question in questions:

                    response = Response.query.filter_by(user_id = user_id, question_id = question.id).first()
                    if response:
                        attempted = True
                        break

                quiz_list.append({
                    'id': quiz.id,
                    'name': quiz.name, 
                    'description': quiz.description,
                    'time_duration': str(quiz.time_duration),
                    'date_of_quiz': str(quiz.date_of_quiz),
                    'attempted': attempted
                })
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

    return subject_data
        
@cache.memoize(timeout=50)
def get_search_results(user_id, query):
    
    subject_data = []
    
    subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f'%{query}%')).all()
    quizzes = Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all()

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
                        'time_duration': str(quiz.time_duration),
                        'date_of_quiz': str(quiz.date_of_quiz),
                    }
                    ch['quizzes'].append(qz)

    # subjects matched by name
    for subject in subjects:
        chapters_ = Chapter.query.filter_by(subject_id = subject.id).all()
        for chapter in chapters_:
            quizzes_ = Quiz.query.filter_by(chapter_id = chapter.id).all()
            for quiz in quizzes_:
                add_to_subject_data(subject, chapter, quiz)
            if not quizzes_:
                add_to_subject_data(subject, chapter)
        if not chapters_:
            add_to_subject_data(subject)

    # chapters matched by name
    for chapter in chapters:
        subject = Subject.query.get(chapter.subject_id)
        quizzes_ = Quiz.query.filter_by(chapter_id=chapter.id).all()
        for quiz in quizzes_:
            add_to_subject_data(subject, chapter, quiz)
        if not quizzes_:
            add_to_subject_data(subject, chapter)

    # quizzes matched by name
    for quiz in quizzes:
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        add_to_subject_data(subject, chapter, quiz)

    return subject_data