# Voice Assistant

A simple cross-platform voice assistant built in Python that can listen to voice commands and respond accordingly.

## Features

- Voice recognition using Google's Speech Recognition API
- Text-to-speech response capability
- Cross-platform support (Windows, macOS, Linux)
- Fallback to text input when microphone isn't available
- Basic commands:
  - Greeting
  - Time and date information
  - Web browser opening
  - Screenshot taking
  - Exit commands

## Prerequisites

- Python 3.6+
- Required Python libraries (see Installation)
- For audio recording/playback:
  - Linux: ffmpeg, mpg123, aplay, or paplay
  - Windows: Default audio playback should work
  - macOS: afplay (built-in)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd assisstant
   ```

2. Install required Python packages:
   ```
   pip install SpeechRecognition gtts pydub pyautogui
   ```

3. Install PyAudio (required for microphone input):
   - Windows/macOS: `pip install PyAudio`
   - Linux:
     ```
     sudo apt-get install portaudio19-dev python3-pyaudio
     pip install PyAudio
     ```

4. Install additional system dependencies (Linux):
   ```
   sudo apt-get install ffmpeg mpg123
   ```

## Usage

### Simple Assistant

Run the simple assistant (optimized for Linux):

```
python simple-assistant.py
```

### Cross-Platform Assistant

Run the cross-platform version (works on Windows, macOS, and Linux):

```
python cross-platform-assistant.py
```

## Available Commands

- "Hello" - Responds with a greeting
- "What time is it?" - Tells the current time
- "What date is it?" - Tells the current date
- "Open browser" or "Browse" - Opens Google in your default web browser
- "Take a screenshot" - Takes a screenshot and saves it as screenshot.png
- "Exit", "Quit", or "Bye" - Exits the assistant

## Troubleshooting

### Microphone Issues

If the assistant can't access your microphone:

1. Make sure your microphone is properly connected and enabled
2. Try running the program with administrator/sudo privileges
3. The program will fall back to text input if needed

### Audio Playback Issues

If you don't hear the assistant's responses:

1. Check your system volume and make sure speakers are connected
2. The program attempts multiple audio playback methods and falls back if needed
3. Audio files are temporarily saved and may need to be manually cleaned up if the program exits unexpectedly

## Extending Functionality

To add new commands, modify the `process_command()` function in either Python file. Add new conditionals to check for your command words and implement the desired functionality.