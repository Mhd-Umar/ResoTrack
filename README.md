# Reso Track - Lab Resource Monitoring System

Reso Track is a web-based application designed for technical institutions to monitor and manage laboratory resources, complaints, and suggestions efficiently.

## Features

- **User Dashboard**: Students can report complaints and submit suggestions.
- **Admin Dashboard**: Main administrators can manage users, labs, and review all submissions.
- **Lab Admin Dashboard**: Lab administrators can manage resources and stocks within their assigned labs.
- **Resource Analyzer**: View and filter resources across different departments and labs.
- **Stock Management**: Track laboratory equipment and supplies.
- **Notification System**: Real-time badges for new complaints and suggestions.

## Technology Stack

- **Framework**: Django
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Icons**: FontAwesome 6
- **Database**: SQLite (default)

## Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd S4_Minor_Project
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run migrations**:
    ```bash
    python manage.py migrate
    ```

5.  **Start the development server**:
    ```bash
    python manage.py runserver
    ```

6.  **Access the application**:
    Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Project Structure

- `project_reso/`: Project configuration and settings.
- `Reso_Track/`: Main application logic (models, views, forms).
- `templates/`: HTML templates.
- `static/`: Static files (CSS, images).
- `media/`: User-uploaded files.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
