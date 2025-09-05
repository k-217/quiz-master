# quiz-master-2


## Description

This project, titled Quiz Master, is a comprehensive evaluation application designed to facilitate effective learning and assessment for both students and educators. It allows users to attempt a variety of timed quizzes tailored to their interest and provides immediate feedback and a detailed history of their performance to track progress over time.

It also allows an admin to control the creation, updating, and deletion of the quizzes and new areas of interest (subjects). It is simple to work with, with a visual appeal and the admin can easily navigate to necessary details from the dashboard. It has a summary option which helps to quickly check through the attempts of a user and the average of different quizzes.

Admin can also control users and can also delete users if unknown to them (say, in a class). This adds to professionalism on the teacher’s (admin) and student’s (user’s) behalf, allowing them to focus on learning better through personalized and timed quizzes.

The ‘user’ side is an even more optimized and appealing one, i.e. from the dashboard, the users can view quizzes, check their scores and their attempted responses with correct answers, and also have a summary of their attempts, either through on the dashboard itself or ask to send a mail of the csv report. The ‘user’ receives daily reminders for the upcoming quizzes and a monthly mail for their previous quiz attempts. 

In all, Quiz Master acts as an exam preparation site for students (‘user’, in the context) and an easy-to-configure quiz platform for a teacher (an admin, say) to analyze their students’ performance.

## Technologies Used

- Backend (Python)
    - flask: lightweight web framework for building scalable web applications
    - flask_sqlalchemy: integrates SQLAlchemy ORM with flask, enabling efficient database modeling and interaction
    - flask-caching: adds caching support, improving performance by storing frequently accessed data
    - flask-security: authentication, authorization, and security features
        - bcrypt: hashing library
    - celery: distributed task queue for handling asynchronous background jobs and scheduling tasks
    - redis: in-memory data store used for caching and as a message broker for celery
    - flask-mailman: simplifies sending emails from flask applications.
    - secure-smtplib: provides secure SMTP connections for sending emails, ensuring encrypted communication
    - pdfkit: converts html content to pdf documents, for creating reports
        - install “wkhtmltopdf” tool before using this
    - python-dotenv: loads environment variables from a .env file, supporting secure and flexible configuration management

- Frontend (HTML + JS)
    - html: structural foundation for web pages and user interfaces
    - css + bootstrap: responsive design, layout, and prebuilt components
    - bootstrap-icons: comprehensive set of vector icons for enhancing elements and user experience
    - vue-js (version 3): progressive javascript framework for building reactive and modular user interfaces
    - vue-router: manages client-side routing, enabling seamless navigation between different views.
    - vue-chartjs: easy creation of interactive charts within vue components
    - chart.js: responsive, customizable charts and data visualizations

- Containerization:
    - docker: packages applications and their dependencies into isolated, portable containers, ensuring consistent environments across development, testing, and production, reducing compatibility issues.


## Steps to Access 

Step 1: Clone the repository.

``` git clone https://github.com/24f2000626/quiz-master-2 ```

Step 2: Check backend/.env and edit the admin credentials and mail settings.

Step 3: Install wkhtmltopdf from web and add its path to backend/tasks.py line 107. 

Step 3: Navigate to the repository and run:

``` docker-compose up --build ```

Step 4: Open any browser and type the below url to enter the application:

``` http://localhost:8080/ ```

## Future Projections

- Allow users to add their preferences for quizzes
- Allow users to share their progress with their friends by making a profile on the platform and enabling messages feature
- Introduce badges, leaderboards, and achievement milestones to motivate and engage users
- Implement AI-driven adaptive quizzes that adjust difficulty based on user performance.
