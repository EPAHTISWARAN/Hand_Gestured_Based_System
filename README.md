📌 Project Overview
This project is an AI-based Hand Gesture Recognition System that uses Computer Vision and Machine Learning techniques to detect and interpret hand gestures in real time. The system captures live video through a webcam, tracks hand landmarks, and performs different system control operations such as volume control, brightness adjustment, cursor movement, and gesture-based interaction.
The project is built using Python along with powerful libraries like OpenCV, MediaPipe, Flask, and PyAutoGUI.


🚀 Features
Real-time hand tracking using webcam
Gesture recognition using MediaPipe
System volume control using hand gestures
Screen brightness control
Mouse movement and click operations
Flask-based backend integration
Cross-Origin support using Flask-CORS
Smooth and responsive gesture detection


🛠️ Technologies Used
Python
Computer Vision
Machine Learning
Flask Framework
OpenCV
MediaPipe


⚙️ System Workflow
Webcam captures live video input.
OpenCV processes the video frames.
MediaPipe detects hand landmarks.
Finger positions are analyzed.
Specific gestures are recognized.
Corresponding system actions are executed:
Cursor movement
Mouse click operations


📂 Project Structure
Bash
AI-Hand-Gesture-System/
│
├── app.py
├── requirements.txt
├── static/
├── templates/
├── assets/
├── README.md
└── model/


🔧 Installation Steps

Step 1: Clone the Repository
Bash
git clone <repository-link>


Step 2: Navigate to Project Folder
Bash
cd AI-Hand-Gesture-System


Step 3: Create Virtual Environment
Bash
python -m venv venv


Step 4: Activate Virtual Environment
Windows
Bash
venv\Scripts\activate
Mac/Linux
Bash
source venv/bin/activate


Step 5: Install Dependencies
Bash
pip install -r requirements.txt


▶️ Running the Project
Bash
python app.py
After running the file:
Webcam will start automatically
Hand gestures will be detected in real time
System controls will respond based on gestures



💡 Applications
Touchless computer interaction
Smart automation systems
Accessibility support
Gaming control systems
Virtual interaction systems




🔮 Future Improvements
Add custom gesture training
Improve gesture accuracy using Deep Learning
Multi-hand gesture support
Integration with IoT devices
Voice and gesture combined control




👨‍💻 Author
Developed as a Computer Vision and AI project for real-time gesture-based system interaction using Python and Machine Learning.
