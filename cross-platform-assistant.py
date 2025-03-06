import os
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import pyautogui
import webbrowser
import subprocess
import tempfile
import time
import platform

def listen_for_command():
    recognizer = sr.Recognizer()
    
    system = platform.system()
    
    try:
        with sr.Microphone() as source:
            print('Listening...')
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        
        try:
            command = recognizer.recognize_google(audio)
            print(f'You said: {command}')
            return command
        except sr.UnknownValueError:
            print('Could not understand audio')
            return None
        except sr.RequestError as e:
            print('Could not request results; {0}'.format(e))
            return None
    
    except (sr.WaitTimeoutError, Exception) as e:
        print(f"Microphone error or timeout: {e}")
        
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_filename = temp_audio.name
        temp_audio.close()
        
        print("Using alternative recording method...")
        
        try:
            if system == "Linux":
                try:
                    subprocess.call([
                        'ffmpeg', 
                        '-y',
                        '-f', 'alsa',
                        '-i', 'default',
                        '-ar', '16000',
                        '-ac', '1',
                        '-t', '5',
                        temp_audio_filename
                    ], stderr=subprocess.DEVNULL)
                except:
                    raise Exception("Recording failed")
                    
            else:  
                print("Automatic recording not available.")
                command = input("Enter your command (text fallback): ")
                print(f'You entered: {command}')
                return command
            
            with sr.AudioFile(temp_audio_filename) as source:
                audio_data = recognizer.record(source)
                
            try:
                command = recognizer.recognize_google(audio_data)
                print(f'You said: {command}')
                return command
            except sr.UnknownValueError:
                print('Could not understand audio')
                return None
            except sr.RequestError as e:
                print('Could not request results; {0}'.format(e))
                return None
        
        except Exception as e:
            print(f"Error recording audio: {e}")

            command = input("Enter your command (text fallback): ")
            print(f'You entered: {command}')
            return command
            
        finally:
            try:
                os.unlink(temp_audio_filename)
            except:
                pass

def listen_with_audio_file():
    recognizer = sr.Recognizer()
    
    print("Record audio with another tool and save as 'input.wav'")
    print("Press Enter when ready to process the file...")
    input()
    
    try:
        if os.path.exists("input.wav"):
            with sr.AudioFile("input.wav") as source:
                print("Processing audio file...")
                audio = recognizer.record(source)
                
            try:
                command = recognizer.recognize_google(audio)
                print('Recognized: ' + command)
                return command
            except sr.UnknownValueError:
                print('Could not understand audio')
                return None
            except sr.RequestError as e:
                print('Could not request results; {0}'.format(e))
                return None
        else:
            print("File 'input.wav' not found")
            return listen_for_command()
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return listen_for_command()

def respond(response_text):
    print(response_text)
    tts = gTTS(text=response_text, lang='en')
    
    system = platform.system()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_filename = temp_file.name
    temp_file.close()
    
    tts.save(temp_filename)
    
    try:
        sound = AudioSegment.from_mp3(temp_filename)
        play(sound)
    except Exception as e:
        print(f"Error playing audio with pydub: {e}")
        
        if system == "Windows":
            try:
                os.startfile(temp_filename)
            except:
                pass
        elif system == "Darwin":  
            try:
                subprocess.call(['afplay', temp_filename])
            except:
                pass
        else:  
            try:
                subprocess.call(['mpg123', '-q', temp_filename])
            except FileNotFoundError:
                if os.system(f'aplay {temp_filename}') != 0:
                    if os.system(f'paplay {temp_filename}') != 0:
                        os.system(f'xdg-open {temp_filename}')
    
    try:
        time.sleep(2) 
        os.unlink(temp_filename)
    except:
        pass

tasks = []
listeningToTask = False

def process_command(command):
    if not command:
        return "I didn't hear anything"
        
    command = command.lower()
    
    if 'hello' in command:
        return "Hello! How can I help you today?"
    elif 'time' in command:
        current_time = time.strftime("%H:%M")
        return f"The current time is {current_time}"
    elif 'date' in command:
        current_date = time.strftime("%Y-%m-%d")
        return f"Today's date is {current_date}"
    elif 'open browser' in command or 'browse' in command:
        webbrowser.open('https://www.google.com')
        return "Opening web browser"
    elif 'screenshot' in command:
        screenshot = pyautogui.screenshot()
        screenshot.save('screenshot.png')
        return "Screenshot taken and saved"
    else:
        return "I'm not sure how to respond to that command"

def main():
    print("Cross-platform Voice Assistant starting...")
    
    while True:
        command = listen_for_command()
        if not command:
            continue
        
        if 'exit' in command or 'quit' in command or 'bye' in command:
            respond("Goodbye!")
            break

        response = process_command(command)
        respond(response)

if __name__ == "__main__":
    main()