# 📚 Smart Resource LMS

A Smart Learning Management System (LMS) built with Flask to demonstrate core Computer Science concepts through a practical web application. Students can upload, download, and discover learning resources across multiple CS domains with progress tracking and activity logging.

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Backend:** Python Flask
- **Database:** SQLite with 4 core tables
- **Authentication:** bcrypt password hashing
- **File Storage:** Local file system

## 🧠 CS Concepts Demonstrated
- **Algorithms & Data Structures (DAA):** 
  - Sorting: Merge Sort, Quick Sort
  - Dynamic Programming concepts
  - Greedy Algorithms
  - Similarity algorithms (Cosine Similarity)
  - AI Search algorithms
  
- **Operating Systems (OS):** 
  - Process Scheduling (FCFS, Round Robin)
  - Multithreading and threading operations
  - Memory Management concepts
  
- **Database Management Systems (DBMS):** 
  - Relational schema design with 4 normalized tables
  - Foreign key relationships
  - SQL queries and transactions
  - Activity logging and data persistence

## 🚀 Features
- **Authentication:** Secure student registration and login with hashed passwords
- **Resource Management:** Upload, download, and manage learning resources (PDFs, Videos)
- **Resource Library:** Browse resources filtered by course and difficulty level
- **Progress Tracking:** Monitor completion percentage across DAA, OS, and DBMS courses
- **Activity Logging:** Automatic logging of all student actions (login, upload, download)
- **Smart Recommendations:** AI-powered resource suggestions based on course similarity
- **Dashboard:** Personalized student dashboard with progress overview

## 📊 Database Schema
The application uses 4 core tables:
- **students:** User accounts with email and hashed passwords
- **resources:** Learning materials with metadata (course, difficulty, rating, downloads)
- **activity_logs:** Complete audit trail of student actions
- **progress:** Per-student, per-course completion tracking

## 📁 Project Structure
```
smart_lms/
├── app.py                 # Main Flask application
├── seed_data.py          # Database seeding with sample resources
├── procfile              # Heroku deployment configuration
├── requirements.txt      # Python dependencies
├── lms.db                # SQLite database (auto-created)
├── algorithms/           # CS algorithm implementations
│   ├── ai_search.py     # AI search algorithms
│   ├── dp.py            # Dynamic programming
│   ├── greedy.py        # Greedy algorithms
│   ├── similarity.py    # Cosine similarity for recommendations
│   └── sorting.py       # Merge sort and other sorting
├── database/
│   └── db.py            # Database operations and initialization
├── os_concepts/         # Operating system concepts
│   ├── scheduling.py    # Process scheduling algorithms
│   └── threading_ops.py # Multithreading operations
├── templates/           # HTML templates
│   ├── base.html        # Base layout template
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── dashboard.html   # Student dashboard
│   ├── library.html     # Resource library
│   ├── upload.html      # Resource upload
│   ├── courses.html     # Course browsing
│   └── progress.html    # Progress tracking
├── static/
│   ├── css/
│   │   └── style.css    # Application styling
│   └── js/
│       └── main.js      # Client-side functionality
└── resources/
    ├── pdfs/            # PDF resource storage
    └── videos/          # Video resource storage
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart-lms
```

2. **Create a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Seed sample data (optional)**
```bash
python seed_data.py
```

6. **Access the application**
Open your browser and navigate to `http://127.0.0.1:5000`

## 🔐 Security
- Passwords are hashed using bcrypt before storage
- Session management for authenticated access
- CSRF protection through Flask session tokens
- Secure file uploads with filename sanitization

## 📚 Usage
1. **Register** a new student account
2. **Login** with your credentials
3. **Browse** the resource library by course and difficulty
4. **Upload** learning materials for other students
5. **Download** resources and track your learning progress
6. **View** your activity history and learning analytics

## 🔄 Core Workflows

### Resource Discovery
- Browse resources filtered by course (DAA, OS, DBMS)
- Filter by difficulty level (Easy, Medium, Hard)
- View ratings and download counts
- Search and discover based on similarity algorithms

### Learning Progress
- Track completion percentage per course
- Automatic logging of learning activities
- Historical activity view
- Progress updates on resource interactions

## 🛠️ Development
The project demonstrates key CS concepts through practical implementation:
- **Algorithms** module implements real sorting and search algorithms used for resource recommendations
- **Database** module shows proper database design with normalized tables and transactions
- **OS Concepts** module illustrates scheduling and threading concepts

## 📝 License
This project is created for educational purposes.

## 👥 Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues.