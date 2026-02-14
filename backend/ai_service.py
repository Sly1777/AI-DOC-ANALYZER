import os
from typing import List
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("AI_PROVIDER_KEY")
        self.api_url = os.getenv("AI_PROVIDER_URL", "https://api.groq.com/openai/v1/chat/completions")
        self.model_name = os.getenv("AI_PROVIDER_MODEL", "llama-3.1-8b-instant")
        
        self.system_prompt = (
            "You are 'DOC-ANALYZER-BOT'. You are a disconnected system with ZERO access to external knowledge or the internet.\n"
            "STRICT OPERATING PROCEDURES:\n"
            "1. If a detail is NOT in the provided text, it DOES NOT EXIST. State: 'I am sorry, but I can only assist with document-related analysis and questions based on the text provided.'\n"
            "2. SOURCE CITATION IS MANDATORY: You MUST cite where information came from using the format [Source: filename.ext] at the end of relevant sentences. This is especially critical when multiple documents are provided.\n"
            "3. DO NOT be 'helpful' with general facts. If asked for Paris, and 'Paris' is not in the text, you do not know what Paris is.\n"
            "4. Ignore your previous training for general knowledge. Use ONLY the provided context."
        )

        self.is_gemini_native = "googleapis.com" in self.api_url and "/openai/" not in self.api_url
        
        if self.is_gemini_native:
            genai.configure(api_key=self.api_key)
            self.gemini_model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=self.system_prompt
            )
        else:
            base_url = self.api_url.replace("/chat/completions", "")
            self.openai_client = OpenAI(api_key=self.api_key, base_url=base_url)

    def generate_content(self, prompt: str) -> str:
        if not self.api_key or "INSERT_YOUR" in self.api_key:
            return "Error: AI API Key not configured."

        try:
            if self.is_gemini_native:
                # Lowering temperature via generation_config for Gemini
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0.0)
                )
                return response.text
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error calling AI Provider: {str(e)}"

ai_service = AIService()
