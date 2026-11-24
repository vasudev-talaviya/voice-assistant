
import speech_recognition as sr
from groq import Groq
import os
import asyncio
import edge_tts
import pygame
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("prompt.txt",'r') as r:
    sys_prompt = r.read()

messages = [
    {
        "role": "system",
        "content": sys_prompt
    }
]

r = sr.Recognizer()

pygame.mixer.init()


def get_ai_response(text):

    messages.append({
        "role": "user",
        "content": text
    })

    completion = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-120b",
        temperature=0
    )

    response = completion.choices[0].message.content

    messages.append({
        "role": "assistant",
        "content": response
    })

    return response


def listen():

    with sr.Microphone() as source:

        r.adjust_for_ambient_noise(source, duration=0.2)

        audio = r.listen(source)

        text = r.recognize_google(audio)

        return text


async def speak(text):

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    audio_data = bytearray()

    async for chunk in communicate.stream():

        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])

    audio_buffer = BytesIO(audio_data)

    try:

        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

    finally:

        pygame.mixer.music.unload()
        audio_buffer.close()
