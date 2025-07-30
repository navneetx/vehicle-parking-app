# **Vehicle Parking App**

A full-stack parking management application built with a Flask backend API and a Vue.js frontend. The application supports role-based access for administrators and regular users, real-time spot management, and background job processing for reports and notifications.

## **Prerequisites**

* Python 3.10+
* Node.js (LTS version recommended)
* Docker Desktop

## **How to Run the Application**

### **1. Initial Setup (From Zip)**

1. Extract the project zip file.
2. Open a **WSL/Ubuntu terminal**.
3. Copy the entire project folder into your WSL home directory to avoid permission issues:  
   # Replace 'YourUsername' with your actual Windows username  
   cp -r /mnt/c/Users/YourUsername/Desktop/vehicle\_parking\_app ~
4. Navigate into the project's new location inside WSL:  
   cd ~/vehicle\_parking\_app
5. Open the project in VS Code connected to WSL:  
   code .

   *From this point, all commands should be run within the terminals of this new VS Code window.*

   ### **2. Backend Setup**

1. Open a new integrated terminal in VS Code (`Ctrl + ``).
2. Navigate to the backend directory:  
   cd backend
3. Create a Python virtual environment:  
   python3 -m venv venv
4. Activate the virtual environment:  
   source venv/bin/activate
5. Install all required Python packages:  
   pip install -r requirements.txt
6. Create the database and the initial admin user:  
   python3 create\_db.py

   ### **3. Frontend Setup**

1. Open a **new** integrated terminal tab in VS Code (`Ctrl + Shift + ``).
2. Navigate to the frontend/ui directory:  
   cd frontend/ui
3. Install all required JavaScript packages:  
   npm install

   ### **4. Running All Services**

   You need **five** processes running simultaneously in separate terminals.

1. **Start Docker Desktop** on your Windows machine.
2. **Start Redis \& Mailhog (in a Windows PowerShell terminal):**  
   # Start Redis Server  
   docker run -d --name redis-server -p 6379:6379 redis/redis-stack:latest

   \# Start Mailhog Server  
   docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog

3. **Start the Backend Servers (in three separate WSL terminals inside the backend folder, with venv activated):**

   * **Terminal 1 (Flask):** python3 app.py
   * **Terminal 2 (Celery Worker):** celery -A celery\_app.celery worker --loglevel=info
   * **Terminal 3 (Celery Beat):** celery -A celery\_app.celery beat --loglevel=info

4. **Start the Frontend Server (in a WSL terminal inside the frontend/ui folder):**

   * **Terminal 4 (Vue):** npm run serve

   ### **Accessing the Application**

* **Web App:** http://localhost:8080
* **Mailhog Inbox (to see emails):** http://localhost:8025

  ### **Default Credentials**

* **Admin:**

  * **Username:** admin
  * **Password:** admin-password123

* **Test User:**

  * **Username:** testuser
  * **Password:** testpassword123
