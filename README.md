# GTAMS: Graduate Teaching Assistant Management System

GTAMS is a comprehensive web application aimed at streamlining the process of managing Graduate Teaching Assistants (GTAs) within a university's department. Built with Flask, GTAMS provides a user-friendly interface for administrative staff and students, ensuring an efficient management process.

## Features

- **User Authentication**: Utilizes Flask-Login for handling user authentication, supporting roles like students, faculty, and admin.
- **Application Submission**: Enables students to apply for GTA positions by submitting detailed applications, including their resumes.
- **Resume Parsing and NLP-based Matching**: Integrates advanced resume parsing functionalities, employing Natural Language Processing (NLP) techniques to automatically extract relevant information from applicants' resumes and match them with job descriptions effectively.
- **Subject Management**: Facilitates administrators in adding, viewing, and managing subjects for GTAs.
- **TA Evaluation**: Allows for the evaluation of teaching assistants by faculty members, ensuring a transparent and efficient review process.

## Technical Stack

- **Backend**: Python with Flask, Flask-WTF for form handling, Flask-Login for session management, Flask-Migrate for database migrations.
- **Database**: SQLite via SQLAlchemy.
- **Frontend**: Bootstrap 5 for responsive UI components and design.
- **NLP Library**: Uses Python NLP libraries for processing and analyzing textual data in resumes and job descriptions.

## Installation and Setup

1. **Ensure Python 3.x is installed**: Verify Python installation with `python --version`.
2. **Clone the repository**: git clone https://github.com/axiom19/GTAMS.git
3. **Navigate to the project directory**: cd GTAMS
4. **Install required Python packages**: pip install -r requirements.txt
5. **Initialize the database**: flask db upgrade
6. **Run the application**: flask run


## Contributing
We welcome contributions from the community. Please use GitHub issues for bug reports, feature requests, or submitting pull requests.



