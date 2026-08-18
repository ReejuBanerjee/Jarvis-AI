from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dotenv import dotenv_values
import os
import mtranslate as mt
import time  

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language.
HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Ensure the Data directory exists.
os.makedirs("Data", exist_ok=True)

# Write the modified HTML code to a file.
with open(r"Data\Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get the absolute file path for the HTML file.
current_dir = os.getcwd()
Link = os.path.abspath("Data/Voice.html").replace("\\", "/")

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument('--log-level=3')

# Initialize the Chrome WebDriver directly via Selenium's native driver management.
driver = webdriver.Chrome(options=chrome_options)

# Load the HTML file once globally.
driver.get("file:///" + Link)

# Define the path for temporary files.
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting status: {e}")

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if not query_words:
        return ""

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    try:
        driver.find_element(by=By.ID, value="start").click()
    except Exception:
        pass

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating ...")
                    return QueryModifier(UniversalTranslator(Text))

        except Exception:
            pass
        
        time.sleep(0.1)

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)