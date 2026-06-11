import speech_recognition as sr
import pyttsx3
import os
import subprocess

engine = pyttsx3.init()
engine.setProperty('rate', 170)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  

def speak(text):
    print(f"🗣️ Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio)
        print(f"👂 You: {command}")
        r
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

def detect_wake_word(command, wake_word="jarvis"):
    return wake_word in command

def handle_commands(command):
    if "open notepad" in command:
        speak("Opening Notepad")
        subprocess.Popen(["notepad.exe"])
    elif "open chrome" in command:
        speak("Opening Google Chrome")
        subprocess.Popen(["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"])
    elif "shutdown" in command or "exit" in command:
        speak("Shutting down. Goodbye!")
        exit()
    else:
        return False  
    return True
