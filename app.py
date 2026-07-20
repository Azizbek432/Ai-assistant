import os
import sys
import time
import ctypes
import asyncio
import datetime
import webbrowser
import pygame
import edge_tts
import speech_recognition as sr
from dotenv import load_dotenv
from google import genai
from google.genai import types

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
os.environ['PYGAME_DETECT_AVX2'] = "1"

ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

try:
    asound = ctypes.cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

client = None
if not API_KEY:
    print("Xato: API kalit topilmadi! .env faylini tekshiring.")
else:
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print(f"Client yaratishda xato: {e}")

system_instruction = (
    "Sen JARVIS-san. Tony Starkning (Temir odam) aqlli sun'iy intellekt yordamchisisan. "
    "Sening xaraktering professional, bir oz kinoyali, sodiq va juda aqlli. "
    "Faqat o'zbek tilida gapir. Foydalanuvchiga 'janob' yoki 'ser' deb murojaat qil. "
    "Har bir fikringni uzog'i 1-2 ta qisqa jumlada ayt, cho'zib o'tirma."
)

pygame.mixer.init()
recognizer = sr.Recognizer()

async def speak_async(text):
    if not text: return
    
    clean_text = text.replace("*", "").replace("#", "")
    sentences = [s.strip() for s in clean_text.split(".") if s.strip()]
    
    for sentence in sentences:
        print(f"JARVIS: {sentence}.")
        file_name = f"j_{int(time.time())}.mp3"
        
        try:
            communicate = edge_tts.Communicate(f"{sentence}.", "uz-UZ-SardorNeural", pitch="-5Hz", rate="+0%")
            await communicate.save(file_name)
            
            pygame.mixer.music.load(file_name)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy(): 
                await asyncio.sleep(0.05)
                
            pygame.mixer.music.unload()
            if os.path.exists(file_name): 
                os.remove(file_name)
                
        except Exception as e:
            print(f"Ovoz chiqarishda xato: {e}")

def speak(text):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(speak_async(text))
        else:
            loop.run_until_complete(speak_async(text))
    except Exception:
        asyncio.run(speak_async(text))

def execute_command(text_command):
    if any(k in text_command for k in ["to'xta", "jim", "o'chir", "toxta"]):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        return True

    if "havo" in text_command:
        speak("Hozir ob-havo ma'lumotlarini tekshiraman, janob.")
        webbrowser.open("https://www.google.com/search?q=ob-havo")
        return True

    if any(k in text_command for k in ["yop", "yo'qot", "stop", "yopa"]):
        if "telegram" in text_command:
            speak("Telegram yopilmoqda.")
            os.system("pkill telegram-desktop")
            return True
        elif any(k in text_command for k in ["kalku", "calcu", "hisob"]):
            speak("Hisoblash tizimi yopilmoqda.")
            os.system("pkill gnome-calculator")
            return True

    is_open_command = any(k in text_command for k in ["och", "ishga tushir", "start"])
    if "telegram" in text_command and (is_open_command or "yop" not in text_command):
        speak("Telegram ishga tushmoqda.")
        os.system("telegram-desktop &")
        return True
    elif any(k in text_command for k in ["kalku", "calcu", "hisob"]) and (is_open_command or "yop" not in text_command):
        speak("Kalkulyator tayyor.")
        os.system("gnome-calculator &")
        return True
    elif "google" in text_command or "brauzer" in text_command:
        speak("Brauzer ochilmoqda.")
        webbrowser.open("https://www.google.com")
        return True

    if any(k in text_command for k in ["qidir", "izla", "youtube", "yutub"]):
        is_youtube = any(y in text_command for y in ["youtube", "yutub"])
        query = text_command.replace("qidir", "").replace("izla", "").replace("youtube", "").replace("yutub", "").strip()
        if is_youtube:
            speak(f"YouTubedan {query} qidirilmoqda.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        else:
            speak(f"Google'dan {query} qidirilmoqda.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    if "soat" in text_command or "vaqt" in text_command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"Hozirgi vaqt {current_time}, janob.")
        return True

    if any(k in text_command for k in ["xayr", "tugat", "dam ol"]):
        speak("Tizim o'chirilmoqda. Xayr, janob.")
        sys.exit()

    return False

def listen_active():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("\n[Jarvis tinglamoqda...]")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language='uz-UZ')
            print(f"Siz: {text}")
            return text.lower().strip()
        except:
            return ""

if __name__ == "__main__":
    current_hour = datetime.datetime.now().hour
    greeting = "Xayrli tong, janob." if current_hour < 12 else "Xayrli kun, ser." if current_hour < 18 else "Xayrli kech, janob."
    speak(f"{greeting} Marhamat.")

    while True:
        voice_text = listen_active()
        
        if not voice_text or len(voice_text) < 2:
            continue
        
        if not execute_command(voice_text):
            if client:
                try:
                    response = client.models.generate_content(
                        model='gemini-1.5-flash', 
                        contents=voice_text,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            max_output_tokens=100
                        )
                    )
                    if response.text:
                        speak(response.text)
                except Exception as e:
                    error_string = str(e)
                    if "429" in error_string:
                        print("[Limit tugadi]")
                        speak("Limit tugadi, janob.")
                    else:
                        print(f"AI Xatosi: {e}")
            else:
                speak("AI tizimi ulanmagan.")