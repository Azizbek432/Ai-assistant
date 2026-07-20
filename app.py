from google import genai
from dotenv import load_dotenv
import speech_recognition as sr
import edge_tts
import pygame
import asyncio
import os
import webbrowser
import time
import datetime
import sys

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

def check_stop_signal():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        try:
            audio = recognizer.listen(source, timeout=1.2, phrase_time_limit=1.2)
            text = recognizer.recognize_google(audio, language='uz-UZ').lower().strip()
            if any(k in text for k in ["to'xta", "jim", "o'chir", "toxta"]):
                return True
        except:
            pass
    return False

async def speak_async(text):
    if not text: return
    
    sentences = [s.strip() for s in text.replace("*", "").split(".") if s.strip()]
    
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
            
        if check_stop_signal():
            print("\n[Ovoz foydalanuvchi buyrug'iga ko'ra to'xtatildi!]")
            break

def speak(text):
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        if loop and loop.is_running():
            loop.create_task(speak_async(text))
        else:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(speak_async(text))
            new_loop.close()
    except Exception as e:
        print(f"Loop xatosi: {e}")

def execute_command(text_command):
    if any(k in text_command for k in ["to'xta", "jim", "o'chir", "toxta"]):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        return True

    if "havo" in text_command:
        speak("Hozir ob-havo ma'lumotlarini tekshiraman, janob.")
        webbrowser.open("https://www.google.com/search?q=ob-havo")
        return True

    if any(k in text_command for k in ["yop", "yo'qot", "stop", "yopa"]):
        if "telegram" in text_command:
            speak("Telegram yopilmoqda.")
            os.system("taskkill /F /IM Telegram.exe /T >nul 2>&1")
            return True
        elif any(k in text_command for k in ["kalku", "calcu", "hisob"]):
            speak("Hisoblash tizimi yopilmoqda.")
            os.system("taskkill /F /IM CalculatorApp.exe /T >nul 2>&1")
            os.system("taskkill /F /IM Calculator.exe /T >nul 2>&1")
            os.system("taskkill /F /IM calc.exe /T >nul 2>&1")
            return True

    is_open_command = any(k in text_command for k in ["och", "ishga tushir", "start"])
    
    if "telegram" in text_command and (is_open_command or "yop" not in text_command):
        speak("Telegram ishga tushmoqda.")
        path = os.path.expanduser("~") + r"\AppData\Roaming\Telegram Desktop\Telegram.exe"
        if os.path.exists(path): os.startfile(path)
        else: os.system("start telegram")
        return True
    elif any(k in text_command for k in ["kalku", "calcu", "hisob"]) and (is_open_command or "yop" not in text_command):
        speak("Kalkulyator tayyor.")
        os.system("start calc.exe")
        return True
    elif "google" in text_command or "brauzer" in text_command:
        speak("Brauzer ochilmoqda.")
        webbrowser.open("https://www.google.com")
        return True

    if any(k in text_command for k in ["qidir", "izla", "yutuq", "youtube", "yutub"]):
        is_youtube = any(y in text_command for y in ["youtube", "yutub", "yutuq"])
        query = text_command.replace("qidir", "").replace("izla", "").replace("dan", "").replace("youtube", "").replace("yutub", "").replace("yutuq", "").strip()
        if is_youtube:
            speak(f"YouTubedan {query} qidirilmoqda.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return True
        else:
            speak(f"Google'dan {query} qidirilmoqda.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return True

    if any(k in text_command for k in ["isming nima", "o'zingni tanishtir", "kim san"]):
        speak("Men Jarvisman, janob. Sizning shaxsiy yordamchingizman.")
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
        print("\n[Jarvis tinglamoqda...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
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
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=voice_text,
                            config={'system_instruction': system_instruction}
                        )
                        if response.text:
                            speak(response.text)
                            break 
                    except Exception as e:
                        error_string = str(e)
                        if "429" in error_string or "RESOURCE_EXHAUSTED" in error_string:
                            print("[429 Xato: Kunlik limit tugadi!]")
                            speak("Kunlik limit tugadi, janob. Mahalliy buyruqlar ishlamoqda.")
                            break
                        elif "503" in error_string and attempt < 2:
                            time.sleep(2) 
                            continue
                        else:
                            print(f"AI Xatosi: {e}")
                            speak("Xatolik yuz berdi, ser.")
                            break
            else:
                speak("AI tizimi o'chiq.")