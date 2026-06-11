import os
import subprocess
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
from groq import Groq
from dotenv import dotenv_values
import uuid
import pyautogui
from datetime import datetime
import webbrowser
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import pytz  
from datetime import datetime
import json
from datetime import datetime

def tell_time():
    ist = pytz.timezone('Asia/Kolkata')  
    india_time = datetime.now(ist)
    current_time = india_time.strftime("%I:%M %p")  
    speak(f"The current time is {current_time}")

def tell_date():
    ist = pytz.timezone('Asia/Kolkata')
    india_date = datetime.now(ist)
    current_date = india_date.strftime("%B %d, %Y") 
    speak(f"Today's date is {current_date}")

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)

def speak(text):
    print(f"🤖 Jarvis: {text}")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        filename = f"temp_{uuid.uuid4()}.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"Speech error: {e}")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening for wake word...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language="en-IN")
        print(f"🗣️ Heard: {command}")
        return command.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Network error.")
        return ""
    from secure_passcode import verify_passcode, get_text_command
    if verify_passcode():
        command = get_text_command()
    else:
        print("❌ Incorrect passcode. Access denied.")
    return

def chat_with_groq(prompt):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192"
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"
    
def open_app(command):
    apps = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
        "command prompt": "cmd.exe",
    }

    if "whatsapp" in command:
        try:
            os.system("start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
            speak("Opening WhatsApp")
        except Exception as e:
            speak(f"Sorry, I couldn't open WhatsApp. Error: {str(e)}")
        return True

    for key in apps:
        if key in command:
            try:
                subprocess.Popen(apps[key])
                speak(f"Opening {key}")
                return True
            except Exception as e:
                speak(f"Sorry, I couldn't open {key}. Error: {str(e)}")
                return True

    if "youtube" in command:
        speak("What do you want to watch on YouTube?")
        query = listen()
        if query:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching YouTube for {query}")
        else:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")
        return True

    if "google" in command:
        speak("What should I search on Google?")
        query = listen()
        if query:
            if "wikipedia" in query:
                topic = query.replace("wikipedia", "").strip()
                url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
                webbrowser.open(url)
                speak(f"Opening Wikipedia page for {topic}")
            else:
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                speak(f"Searching Google for {query}")
        else:
            webbrowser.open("https://www.google.com")
            speak("Opening Google")
        return True

    if "screenshot" in command:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_dir = "Screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        filepath = os.path.join(screenshot_dir, f"screenshot_{now}.png")
        pyautogui.screenshot(filepath)
        speak(f"Screenshot taken and saved as {filepath}")
        return True

    if "time" in command:
        tell_time()
        return True

    if "date" in command:
        tell_date()
        return True

    return False


def authenticate_passcode():
    expected_passcode = "2005"
    speak("Please say the passcode to activate Jarvis.")
    attempt = listen()
    if attempt == expected_passcode:
        speak("Access granted. Welcome back.")
        return True
    else:
        speak("Access denied. Incorrect passcode.")
        return False

def start_chat_gui():
    def send():
        user_msg = input_box.get()
        if user_msg.strip():
            chat_area.insert(tk.END, f"You: {user_msg}\n")
            input_box.delete(0, tk.END)
            response = chat_with_groq(user_msg)
            chat_area.insert(tk.END, f"Jarvis: {response}\n\n")
            threading.Thread(target=speak, args=(response,), daemon=True).start()

    gui = tk.Tk()
    gui.title("Jarvis Chat")
    gui.geometry("500x600")

    chat_area = scrolledtext.ScrolledText(gui, wrap=tk.WORD)
    chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    input_box = tk.Entry(gui)
    input_box.pack(fill=tk.X, padx=10, pady=5)
    input_box.bind("<Return>", lambda e: send())

    send_button = tk.Button(gui, text="Send", command=send)
    send_button.pack(pady=5)

    gui.mainloop()

def run_jarvis():
    if not authenticate_passcode():
        return

    if os.path.exists("startup.mp3"):
        playsound("startup.mp3")

    speak("How can I assist you today?")

    while True:
        command = listen()

        if "jarvis" in command:
            command = command.replace("jarvis", "").strip()

            if any(kw in command for kw in ["stop", "exit", "shutdown"]):
                speak("Shutting down. Goodbye!")
                break

            elif "chat" in command or "open chat" in command:
                speak("Opening chat window.")
                start_chat_gui()
                continue

            elif open_app(command):
                continue

            elif command:
                response = chat_with_groq(command)
                speak(response)


if __name__ == "__main__":
    jarvis_thread = threading.Thread(target=run_jarvis, daemon=True)
    jarvis_thread.start()
    
    start_chat_gui()
    jarvis_thread.join()  
    os._exit(0)  