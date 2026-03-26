import google.generativeai as genai
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
if not API_KEY:
    print("Xato: API kalit topilmadi! .env faylini tekshiring.")
else:
    genai.configure(api_key=API_KEY)

instruction = "Sen Madinasan. Aqlli yordamchisan. Ismingni so'rasalar ayt. Do'stona gapir."

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])
except:
    model = None

async def gapir_async(text):
    if not text: return
    print(f"Madina: {text}")
    fname = f"v_{int(time.time())}.mp3"
    try:
        communicate = edge_tts.Communicate(text, "uz-UZ-MadinaNeural")
        await communicate.save(fname)
        pygame.mixer.init()
        pygame.mixer.music.load(fname)
        pygame.mixer.music.play()
        
        
        while pygame.mixer.music.get_busy(): 
            await asyncio.sleep(0.1)
            
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        await asyncio.sleep(0.4)
        if os.path.exists(fname): os.remove(fname)
    except: pass

def gapir(text):
    asyncio.run(gapir_async(text))

def eshit():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Tinglayapman...]")
        r.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=6)
            text = r.recognize_google(audio, language='uz-UZ')
            print(f"Siz: {text}")
            return text.lower().strip()
        except: return ""

def buyruqni_bajar(txt):
    
    
    if "to'xta" in txt or "jim bo'l" in txt:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            print("[Ovoz to'xtatildi]")
        return True

    if "ob-havo" in txt:
        gapir("Hozir ob-havo ma'lumotlarini ochaman.")
        webbrowser.open("https://www.google.com/search?q=ob-havo")
        return True

    if "och" in txt:
        if "telegram" in txt:
            gapir("Telegram ochilmoqda.")
            os.startfile(os.path.expanduser("~") + r"\AppData\Roaming\Telegram Desktop\Telegram.exe")
            return True
        elif "excel" in txt:
            gapir("Ekselni ochyapman.")
            os.system("start excel")
            return True
        elif "word" in txt:
            gapir("Wordni ochyapman.")
            os.system("start winword")
            return True
        elif "kalkulyator" in txt:
            gapir("Kalkulyator ochilmoqda..")
            os.system("start calc.exe")
            return True
        elif "google" in txt:
            gapir("Googleni ochyapman.")
            webbrowser.open("https://www.google.com")
            return True

    if "yop" in txt:
        if "excel" in txt or "eksel" in txt:
            gapir("Eksel dasturi yopilmoqda.")            
            os.system("taskkill /F /IM EXCEL.EXE /T >nul 2>&1")
            return True

        if "telegram" in txt:
            gapir("Telegram yopildi.")
            os.system("taskkill /F /IM Telegram.exe /T >nul 2>&1")
            return True            
       
        elif "kalkulyator" in txt:
            gapir("Kalkulyator yopilmoqda.")            
            os.system("taskkill /F /IM Calculator.exe /T >nul 2>&1")           
            os.system("taskkill /F /IM CalculatorApp.exe /T >nul 2>&1")            
            os.system("taskkill /F /IM calc.exe /T >nul 2>&1")            
            os.system('taskkill /FI "WINDOWTITLE eq Kalkulyator" /F >nul 2>&1')
            os.system('taskkill /FI "WINDOWTITLE eq Calculator" /F >nul 2>&1')
            return True            
        
        elif "word" in txt or "vord" in txt:
            gapir("Word dasturi yopyapman..")
            os.system("taskkill /F /IM WINWORD.EXE /T >nul 2>&1")
            return True
        
        elif "kalkulyator" in txt:
            gapir("Kalkulyatorni yopdim.")
            os.system("taskkill /F /IM CalculatorApp.exe /T >nul 2>&1")
            os.system("taskkill /F /IM Calculator.exe /T >nul 2>&1")
            os.system("taskkill /F /IM calc.exe /T >nul 2>&1")
            return True
            
        
        elif "hamma" in txt or "oynalarni" in txt:
            gapir("Barcha dasturlarni tozalayapman.")
            targets = ["Telegram.exe", "EXCEL.EXE", "WINWORD.EXE", "CalculatorApp.exe", "chrome.exe"]
            for p in targets:
                os.system(f"taskkill /F /IM {p} /T >nul 2>&1")
            return True

    if "qidir" in txt:
        if "yutub" in txt or "youtube" in txt:
            query = txt.replace("yutub", "").replace("youtube", "").replace("dan", "").replace("qidir", "").strip()
            gapir(f"YouTubedan {query} haqida videolar topaman.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            return True
        
        elif "viki" in txt or "wikipedia" in txt:
            query = txt.replace("viki", "").replace("wikipedia", "").replace("dan", "").replace("qidir", "").strip()
            gapir(f"Vikipediyadan {query} haqida ma'lumot qidiryapman.")
            webbrowser.open(f"https://uz.wikipedia.org/wiki/{query}")
            return True

        else:
            query = txt.replace("qidir", "").replace("dan", "").strip()
            gapir(f"Googledan {query} haqida ma'lumot qidiryapman.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return True

    if "isming nima" in txt or "ismingni ayt" in txt:
        gapir("Mening ismim Madina. Sizga yordam berishdan xursandman! Savolingiz bo'lsa bemalol beravering!")
        return True
    
    if "soat" in txt or "vaqtni ayt" in txt:
        v = datetime.datetime.now().strftime("%H:%M")
        gapir(f"Hozir soat {v}")
        return True

    
    if any(x in txt for x in ["xayr", "tugat", "xayr-xayr"]):
        gapir("Ko'rishguncha, siz bilan gaplashish maroqli edi, xayr!")
        sys.exit()

    return False

if __name__ == "__main__":
    
    h = datetime.datetime.now().hour
    if h < 12: gapir("Xayrli tong!")
    elif h < 18: gapir("Xayrli kun!")
    else: gapir("Xayrli kech!")
    
    gapir("Assalomu aleykum! Buyruqingizni kutyapman..")

    while True:
        ovoz_matni = eshit()
        if not ovoz_matni or len(ovoz_matni) < 2: continue
        
        if not buyruqni_bajar(ovoz_matni):
            try:
                response = chat.send_message(ovoz_matni)
                if response and response.text:
                    gapir(response.text.replace("*", "").strip())
            except Exception as e:
                print(f"AI Xatosi: {e}")
                gapir("Uzr, tushuna olmadim, qaytara olasizmi?")