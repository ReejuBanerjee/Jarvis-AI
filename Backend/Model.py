# System // Jarvis Neural Core
# Module: Advanced Decision-Making Model (First Layer) - Groq Unified

import logging
from rich import print
from dotenv import dotenv_values
from groq import Groq
from typing import List

# Setup professional logging for silent error tracking
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables safely
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    print("[bold red]CRITICAL ERROR: GroqAPIKey not found in .env file![/bold red]")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Define recognized function keywords for precise task categorization.
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

def FirstLayerDMM(prompt: str = "test") -> List[str]:
    """
    Analyzes the user prompt and classifies it into actionable system commands using Groq.
    Returns a list of parsed command strings.
    """
    try:
        # Brutally strict system prompt to force exact string matching
        system_prompt = """
        You are a backend routing model. Your ONLY job is to classify the user's input into specific function strings.
        DO NOT talk, converse, or explain. ONLY output the formatted strings separated by commas.
        
        Routing Categories:
        - 'general [query]' : For chatting, general questions, and facts.
        - 'realtime [query]' : For live data, current weather, or recent news.
        - 'open [app]' : To open an application or website.
        - 'close [app]' : To close an application.
        - 'play [song]' : To play a song or video on YouTube.
        - 'generate image [prompt]' : To generate an image.
        - 'system [task]' : For hardware controls (mute, unmute, volume up, volume down).
        - 'content [topic]' : To write text, emails, essays, or code.
        - 'google search [topic]' : To search Google.
        - 'youtube search [topic]' : To search YouTube.
        - 'exit' : If the user says goodbye or quit.
        
        Strict Rules:
        1. If input is "play baby on youtube", output EXACTLY: play baby
        2. If input is "search who is narendra modi on google", output EXACTLY: google search who is narendra modi
        3. If multiple tasks: "open chrome and play despacito" -> output: open chrome, play despacito
        4. If unrecognized or ambiguous, default to: general [query]
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # FIXED: Swapped to an actively supported production model on Groq
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.0, 
            max_tokens=1024
        )

        response = completion.choices[0].message.content

        # Clean and parse the response string safely
        response = response.replace("\n", " ")
        raw_tasks = response.split(",")
        cleaned_tasks = [task.strip().lower().replace(".", "").replace("?", "").replace("!", "") for task in raw_tasks]

        valid_tasks = []
        for task in cleaned_tasks:
            for func in funcs:
                if task.startswith(func):
                    valid_tasks.append(task)
                    break 

        if not valid_tasks:
            return [f"general {prompt}"]

        return valid_tasks

    except Exception as e:
        logging.error(f"Groq DMM Execution Failed: {e}")
        return [f"general {prompt}"]

if __name__ == "__main__":
    print("[bold cyan]Jarvis DMM Module Initialized. Type a query to test classification.[/bold cyan]")
    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            print(FirstLayerDMM(user_input))
        except KeyboardInterrupt:
            print("\nExiting DMM test environment.")
            break