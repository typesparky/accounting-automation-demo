import os
import requests
import json
import base64
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class OpenRouterConnector:
    """
    Connector for OpenRouter API to access Google Gemini and other models.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or provided.")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://termeer-group.com", # Optional, for OpenRouter rankings
            "X-Title": "Termeer Accounting Automation", # Optional
            "Content-Type": "application/json"
        }

    def chat(self, model: str, messages: List[Dict[str, Any]], stream: bool = False) -> Dict[str, Any]:
        """
        Sends a chat completion request to OpenRouter.
        """
        payload = {
            "model": model,
            "messages": messages,
        }
        
        response = requests.post(
            self.base_url,
            headers=self._get_headers(),
            data=json.dumps(payload)
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter Error {response.status_code}: {response.text}")
            
        return response.json()

    def vision_chat(self, model: str, prompt: str, image_b64: str) -> Dict[str, Any]:
        """
        Sends a vision-based completion request with a base64 encoded image.
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]
        return self.chat(model, messages)

    def vision_chat_multi(self, model: str, system_prompt: str, user_prompt: str, images_b64: List[str]) -> Dict[str, Any]:
        """
        Sends a vision-based request with MULTIPLE images (all pages of a PDF).
        Uses a system message for the extraction rules and a user message with images.
        """
        content_parts = [{"type": "text", "text": user_prompt}]
        for img_b64 in images_b64:
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                }
            })
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_parts}
        ]
        return self.chat(model, messages)
