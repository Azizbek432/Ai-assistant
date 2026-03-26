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

instruction = (
    "Sen JARVIS-san. Tony Starkning (Temir odam) aqlli sun'iy intellekt yordamchisisan. "
    "Sening xaraktering professional, bir oz kinoyali, sodiq va juda aqlli. "
    "Faqat o'zbek tilida gapir. Foydalanuvchiga 'janob' yoki 'ser' deb murojaat qil."
)

try:
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=instruction)
    chat = model.start_chat(history=[])
except Exception as e:
    print(f"Model yuklashda xato: {e}")
    chat = None

pygame.mixer.init()

async def gapir_async(text):
    if not text: return
    tozalangan_matn = text.replace("*", "").strip()
    print(f"JARVIS: {tozalangan_matn}")
    
    fname = f"j_{int(time.time())}.mp3"
    try:
        communicate = edge_tts.Communicate(tozalangan_matn, "uz-UZ-SardorNeural", pitch="-5Hz", rate="+0%")
        await communicate.save(fname)
        
        pygame.mixer.music.load(fname)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy(): 
            await asyncio.sleep(0.1)
            
        pygame.mixer.music.unload()
        if os.path.exists(fname): 
            os.remove(fname)
    except Exception as e:
        print(f"Ovoz chiqarishda xato: {e}")

def gapir(text):
    """Sinxron funksiya orqali asinxron gapirishni ishga tushirish"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(gapir_async(text))
        else:
            asyncio.run(gapir_async(text))
    except RuntimeError:
        asyncio.run(gapir_async(text))

def eshit():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Jarvis tinglamoqda...]")
        r.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=6)
            text = r.recognize_google(audio, language='uz-UZ')
            print(f"Siz: {text}")
            return text.lower().strip()
        except:
            return ""

def buyruqni_bajar(txt):
    if any(x in txt for x in ["to'xta", "jim bo'l", "ovozni o'chir"]):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            print("[Ovoz to'xtatildi]")
        return True

    if "ob-havo" in txt:
        gapir("Hozir ob-havo ma'lumotlarini tekshiraman, janob.")
        webbrowser.open("https://www.google.com/search?q=ob-havo")
        return True

    if "och" in txt:
        if "telegram" in txt:
            gapir("Telegram xabarlar tizimi ishga tushmoqda.")
            path = os.path.expanduser("~") + r"\AppData\Roaming\Telegram Desktop\Telegram.exe"
            if os.path.exists(path): os.startfile(path)
            else: os.system("start telegram")
            return True
        elif "kalkulyator" in txt:
            gapir("Hisoblash tizimi tayyor, ser.")
            os.system("start calc.exe")
            return True
        elif "google" in txt:
            gapir("Global tarmoqqa ulanmoqdaman.")
            webbrowser.open("https://www.google.com")
            return True

    if "qidir" in txt:
        query = txt.replace("qidir", "").replace("dan", "").replace("youtube", "").replace("yutub", "").strip()
        if "youtube" in txt or "yutub" in txt:
            gapir(f"YouTubedan {query} bo'yicha vizual ma'lumotlar topildi.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        else:
            gapir(f"Ma'lumotlar bazasidan {query} qidirilmoqda.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        return True

    if any(x in txt for x in ["isming nima", "o'zingni tanishtir", "kim san"]):
        gapir("Men Jarvisman, janob. Sizning shaxsiy yordamchingizman. Barcha tizimlar nazorat ostida.")
        return True

    if "soat" in txt or "vaqt" in txt:
        v = datetime.datetime.now().strftime("%H:%M")
        gapir(f"Hozirgi vaqt {v}, janob.")
        return True

    if any(x in txt for x in ["xayr", "tugat", "dam ol"]):
        gapir("Tizimlar o'chirilmoqda. Xayr, janob.")
        sys.exit()

    return False

if __name__ == "__main__":
    h = datetime.datetime.now().hour
    if h < 12: salom = "Xayrli tong, janob."
    elif h < 18: salom = "Xayrli kun, ser. Tizimlar tayyor."
    else: salom = "Xayrli kech, janob."
    
    gapir(f"{salom} Men Jarvisman. Buyruqingizni kutyapman.")

    while True:
        ovoz_matni = eshit()
        if not ovoz_matni or len(ovoz_matni) < 2:
            continue
        
        if not buyruqni_bajar(ovoz_matni):
            try:
                if chat:
                    response = chat.send_message(ovoz_matni)
                    gapir(response.text)
                else:
                    gapir("Kechirasiz ser, AI moduli bilan aloqa uzilgan.")
            except Exception as e:
                print(f"AI Xatosi: {e}")
                gapir("Tizimda xatolik yuz berdi. Qaytadan urinib ko'ring.")