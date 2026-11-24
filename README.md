# 🤖 J.A.R.V.I.S – Voice AI Assistant v3.0

### Just A Rather Very Intelligent System

An intelligent voice-controlled desktop assistant built using Python that helps users interact with their computers through voice commands. J.A.R.V.I.S can open and close applications, search the internet, play YouTube videos, monitor system performance, manage basic system operations, and respond through speech.

---

## 🚀 Project Overview

J.A.R.V.I.S is a Python-based Voice AI Assistant developed as a Final Year Project. It uses speech recognition and text-to-speech technologies to provide a hands-free desktop experience.

The assistant listens to user commands through a microphone, processes the recognized speech, and performs the requested actions. It also features a futuristic HUD (Heads-Up Display) interface inspired by Iron Man.

## ✨ Features

- 🎙️ **Voice Recognition** – Recognizes voice commands using Google Speech Recognition.
- 🗣️ **Voice Response** – Responds to users using text-to-speech.
- 💻 **Application Control** – Opens and closes desktop applications.
- 🌐 **Web Browsing** – Opens websites and performs Google searches.
- 🎵 **YouTube Integration** – Searches and plays songs or videos on YouTube.
- 📚 **Wikipedia Search** – Retrieves short information about topics.
- 🔋 **Battery Monitoring** – Displays battery percentage and charging status.
- 📊 **System Monitoring** – Checks CPU and RAM usage.
- 📸 **Screenshot Capture** – Takes screenshots using voice commands.
- ⚙️ **System Management** – Supports shutdown, restart, sleep, and screen lock.
- 🔊 **Volume Control** – Supports volume up, volume down, and mute on Windows.
- 🕒 **Time & Date** – Provides current time and date.
- 😂 **Entertainment** – Tells random programming and general jokes.
- 🎨 **Iron Man HUD Interface** – Displays an animated futuristic interface with system status.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core Programming Language |
| SpeechRecognition | Voice Recognition |
| pyttsx3 | Text-to-Speech |
| OpenCV | HUD Interface |
| NumPy | Image Processing |
| Pillow | Image and GIF Handling |
| Wikipedia API | Information Retrieval |
| psutil | System Monitoring |
| PyAutoGUI | Screenshot Capture |
| Threading | Background Execution |

## 📂 Project Structure

```text
JARVIS-Voice-AI-Assistant/
│
├── jarvis_ai.py       # Main Python application
├── jarvis.gif         # Optional animated HUD background
├── ironman.gif        # Alternative GIF background
├── README.md          # Project documentation
└── requirements.txt   # Python dependencies (optional)
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/JARVIS-Voice-AI-Assistant.git
```

### 2. Navigate to the Project Folder

```bash
cd JARVIS-Voice-AI-Assistant
```

### 3. Install Required Libraries

```bash
pip install SpeechRecognition pyttsx3 opencv-python numpy pillow wikipedia psutil pyautogui
```

**Additional requirements:**
- A working microphone is required.
- PyAudio or a compatible microphone audio backend may be required for microphone access.
- `pywin32` is required for Windows volume control.

Install Windows volume-control support using:

```bash
pip install pywin32
```

### 4. Run the Application

```bash
python jarvis_ai.py
```

### 5. Launch J.A.R.V.I.S

- Allow microphone access.
- Ensure your microphone is connected.
- Place `jarvis.gif` in the project folder for the animated HUD background.
- Start giving voice commands.

**Note:** The application can use an animated fallback background if the GIF is unavailable. OpenCV is required for the graphical HUD.

## 🎤 Voice Commands

Here are some example commands you can use:

| Voice Command | Action |
|---|---|
| Hey Jarvis, open Chrome | Opens Google Chrome |
| Open Notepad | Opens Notepad |
| Open VS Code | Launches Visual Studio Code |
| Open Calculator | Opens Calculator |
| Play Believer | Searches and plays on YouTube |
| What is Python? | Retrieves information from Wikipedia |
| Search Java Programming | Searches Google |
| What time is it? | Announces current time |
| What is today's date? | Announces current date |
| Battery status | Checks battery information |
| CPU status | Displays CPU and RAM usage |
| Take screenshot | Captures a screenshot |
| What is my IP address? | Displays local IP address |
| Close Spotify | Closes Spotify |
| Lock screen | Locks the computer |
| Volume up | Increases system volume (Windows) |
| Tell me a joke | Tells a random joke |
| Shutdown | Initiates system shutdown |
| Restart | Restarts the computer |
| Sleep | Puts the computer to sleep |
| Bye | Exits J.A.R.V.I.S |

**To exit:** Say "Bye", "Exit", or press `Q` / `ESC` in the HUD window.

## 🧠 How It Works

The J.A.R.V.I.S system follows a simple voice-processing workflow:

1. **Voice Input:** Captures the user's voice through a microphone.
2. **Speech Recognition:** Converts spoken words into text.
3. **Command Processing:** Identifies the user's requested action.
4. **Command Execution:** Performs the corresponding system or web operation.
5. **Voice Output:** Provides a spoken response using the text-to-speech engine.
6. **HUD Display:** Updates the graphical interface with the current status and response.

## 🎯 Project Objectives

- Develop a voice-controlled desktop assistant using Python.
- Reduce manual keyboard and mouse interactions.
- Automate common desktop operations.
- Integrate speech recognition and speech synthesis.
- Provide real-time system monitoring.
- Create an interactive and futuristic user interface.

## 🔮 Future Enhancements

- Integration with advanced AI language models.
- Natural Language Processing improvements.
- Offline speech recognition.
- Smart home device integration.
- Personalized voice responses.
- Improved security and user authentication.
- Advanced automation and task scheduling.

## ⚠️ Important Notes

- Google Speech Recognition requires an active internet connection.
- Wikipedia searches require internet connectivity.
- Some desktop applications depend on the operating system and installed software.
- Battery information is available only on supported devices.
- Shutdown and restart commands execute actual operating-system actions. Use them carefully.
- Certain features require optional Python packages.

## 👨‍💻 Developer

**Developed as a Final Year Project**

**Project Name:** J.A.R.V.I.S – Voice AI Assistant  
**Version:** 3.0  
**Programming Language:** Python  
**Project Domain:** Artificial Intelligence / Voice Automation / Desktop Automation

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, Automation, and a Vision for Intelligent Assistance.** 🤖
