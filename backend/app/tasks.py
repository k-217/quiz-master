from flask_mailman import EmailMessage
from app.extensions import db, celery
from app.models.models import User, Quiz, Score, Subject, Chapter, Role
from datetime import datetime
import csv
from io import StringIO
import pdfkit
from jinja2 import Template

from celery.schedules import crontab

celery.conf.update(
    beat_schedule = {
        'daily-reminders': {
            'task': 'app.tasks.send_daily_reminders',
            'schedule': crontab(hour = 5, minute = 00),
        },
        'monthly-reports': {
            'task': 'app.tasks.generate_monthly_reports',
            'schedule': crontab(hour = 8, minute = 00, day_of_month = 12),
        },
    }
)

@celery.task()
def send_daily_reminders():
    
    # sends daily quiz reminders at 5pm
    
    users = User.query.join(User.roles).filter(Role.name == 'user').all()

    upcoming_quizzes = Quiz.query.filter(
        Quiz.date_of_quiz > datetime.now()
    ).limit(3).all()

    if upcoming_quizzes:

        for user in users:

            try:
        
                email = EmailMessage(
                    subject = "Daily Quiz Reminder",
                    body = f"Hi {user.username}, \n\nYou have {len(upcoming_quizzes)} upcoming quizzes:\n"  + 
                        "\n".join([f"- {q.name} on {q.date_of_quiz.strftime('%b %d')}" for q in upcoming_quizzes]),
                    to = [user.email]
                )
                email.send()
            
            except Exception as e:
                return 

@celery.task()
def generate_monthly_reports():
    
    # generates and sends monthly reports on the 1st of each month

    users = User.query.join(User.roles).filter(Role.name == 'user').all()
    
    for user in users:
        
        report_data = {
            "user": user,
            "month": datetime.now().strftime("%B %Y"),
            "quiz_attempts": Score.query.filter_by(user_id = user.id).count(),
            "avg_score": db.session.query(db.func.avg(Score.total_score)).filter_by(user_id = user.id).scalar() or 0,
        }

        html_report = render_html_report(report_data)
        
        pdf_report = generate_pdf_report(html_report)
        
        email = EmailMessage(
            subject = f"Monthly Activity Report - {report_data['month']}",
            body = f"Hi, {user.username}! Your monthly learning activity report is attached. Keep Learning!",
            to = [user.email]
        )
        email.attach("report.html", html_report, "text/html")
        email.attach("report.pdf", pdf_report, "application/pdf")
        email.send()

def render_html_report(data):
    
    # template -> html

    template = Template("""
    <!DOCTYPE html>
    <html>
    <head> <title> Monthly Report </title> </head>
    <body>
        <h1> Learning Report for {{ data.user.username }} - {{ data.month }} </h1>
        <p> Quiz Attempts: {{ data.quiz_attempts }} </p>
        <p> Average Score: {{ "%.2f"|format(data.avg_score) }}% </p>
    </body>
    </html>
    """)

    return template.render(data = data)

def generate_pdf_report(html_content):
    
    # html -> pdf

    return pdfkit.from_string(
        html_content, 
        False, 
        configuration = pdfkit.configuration(wkhtmltopdf = 'C:/Users/kanis/Downloads/wkhtmltopdf/bin/wkhtmltopdf.exe')
    )

@celery.task()
def export_user_quiz_data(user_id):
    
    # exports user's quiz history to csv

    user = User.query.get(user_id)
    if not user:
        return

    # prepare csv data
    csv_data = StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["Subject", "Chapter", "Quiz", "Score", "Date Attempted"])
    
    scores = Score.query.filter_by(user_id=user_id).all()
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        writer.writerow([
            subject.name,
            chapter.name,
            quiz.name,
            score.total_score,
            score.time_of_attempt.strftime("%Y-%m-%d")
        ])
    
    email = EmailMessage(
        subject = "Your Quiz History Export",
        body = "Your quiz history is attached as CSV",
        to = [user.email]
    )
    email.attach("quiz_history.csv", csv_data.getvalue(), "text/csv")
    email.send()
    return {"status": "completed", "user_id": user_id}
