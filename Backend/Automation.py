from AppOpener import close, open as appopen
import pywhatkit as kit
from dotenv import dotenv_values
from googlesearch import search 
from rich import print
from groq import Groq
import webbrowser
import subprocess
import keyboard
import asyncio
import os

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User") 

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Helper function to forcefully open URLs in Google Chrome by finding the exact .exe
def ForceChrome(url):
    # Standard Windows Google Chrome installation paths
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    try:
        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                # We found Chrome! Register it and force it to open the URL
                webbrowser.register('force_chrome', None, webbrowser.BackgroundBrowser(path))
                webbrowser.get('force_chrome').open(url)
                chrome_found = True
                break
                
        if not chrome_found:
            # If Chrome isn't installed in a standard location, fallback to the default browser
            print("Chrome not found in standard paths. Falling back to system default.")
            webbrowser.open(url)
            
    except Exception as e:
        print(f"Failed to force Chrome: {e}")
        webbrowser.open(url) # Ultimate safety fallback

# Function to perform a Google search.
def GoogleSearch(Topic):
    ForceChrome(f"https://www.google.com/search?q={Topic}") 
    return True 

# Function to generate content using AI and save it to a file.
def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe' 
        subprocess.Popen([default_text_editor, File]) 

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"}) 

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=SystemChatBot + messages, 
            max_tokens=2048, 
            temperature=0.7, 
            top_p=1, 
            stream=True, 
            stop=None 
        )

        Answer = "" 

        for chunk in completion:
            if chunk.choices[0].delta.content: 
                Answer += chunk.choices[0].delta.content 

        Answer = Answer.replace("</s>", "") 
        messages.append({"role": "assistant", "content": Answer}) 
        return Answer

    Topic = str(Topic).replace("Content ", "") 
    ContentByAI = ContentWriterAI(Topic) 

    os.makedirs("Data", exist_ok=True) 
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI) 
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt") 
    return True 

# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    ForceChrome(f"https://www.youtube.com/results?search_query={Topic}")
    return True 

# Function to play a video on YouTube.
def PlayYouTube(query):
    kit.playonyt(query) 
    return True 

# Function to open an application or FORCE search Google Chrome if missing.
def OpenApp(app):
    app_lower = app.lower().strip()
    
    # Handle common local app aliases
    if app_lower == "chrome":
        app = "google chrome"

    try:
        # 1. ALWAYS attempt to open the app locally FIRST.
        appopen(app, match_closest=False, output=False, throw_error=True) 
        return True 
    
    except Exception:
        # 2. If the app isn't found locally, forcefully route to Chrome
        print(f"App '{app}' not found locally. Forcing Google Chrome to open...")
        
        # Fast-track dictionary for instant web opening of known platforms
        common_web_apps = {
            "instagram": "https://www.instagram.com",
            "whatsapp": "https://web.whatsapp.com",
            "facebook": "https://www.facebook.com",
            "youtube": "https://www.youtube.com",
            "twitter": "https://www.twitter.com",
            "x": "https://www.x.com",
            "github": "https://www.github.com",
            "linkedin": "https://www.linkedin.com",
            "discord": "https://discord.com/app",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "reddit": "https://www.reddit.com",
            "chatgpt": "https://chatgpt.com",
            "amazon": "https://www.amazon.in"
        }
        
        if app_lower in common_web_apps:
            ForceChrome(common_web_apps[app_lower])
            return True
        else:
            # 3. If it's an unknown app, search it on Google and grab the top link
            try:
                top_links = list(search(app, num_results=1))
                if top_links:
                    ForceChrome(top_links[0])
                    return True
            except:
                # Ultimate fallback: Opens a Google search tab with the app name
                ForceChrome(f"https://www.google.com/search?q={app}")
                return True

# Function to close an application.
def CloseApp(app):
    if "chrome" in app:
        pass 
    else:
        try:
            close(app, match_closest=True, output=False, throw_error=True) 
            return True 
        except:
            return False 

# Function to execute system-level commands.
def System(command):
    
    def mute():
        keyboard.press_and_release("volume mute") 

    def unmute():
        keyboard.press_and_release("volume mute") 

    def volume_up():
        keyboard.press_and_release("volume up") 

    def volume_down():
        keyboard.press_and_release("volume down") 

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True 

# Asynchronous function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):
    funcs = [] 

    for command in commands:
        if command.startswith("open "): 
            if "open it" in command: 
                pass
            elif "open file" in command: 
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open ")) 
                funcs.append(fun)

        elif command.startswith("general "): 
            pass
        elif command.startswith("realtime "): 
            pass
        elif command.startswith("close "): 
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close ")) 
            funcs.append(fun)
        elif command.startswith("play "): 
            fun = asyncio.to_thread(PlayYouTube, command.removeprefix("play ")) 
            funcs.append(fun)
        elif command.startswith("content "): 
            fun = asyncio.to_thread(Content, command.removeprefix("content ")) 
            funcs.append(fun)
        elif command.startswith("google search "): 
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "): 
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")) 
            funcs.append(fun)
        elif command.startswith("system "): 
            fun = asyncio.to_thread(System, command.removeprefix("system ")) 
            funcs.append(fun)
        else:
            print(f"No Function Found. For {command}") 

    results = await asyncio.gather(*funcs) 

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands): 
        pass

    return True