from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import re

load_dotenv()

class GeminiService:
    def __init__(self):
        # Using latest SDK
        self.client = genai.Client()
    
    def analyze_news_preference(self, news_article: dict, user_preference: str) -> dict:
        """Analyze how much the user might like this news based on their preference"""
        
        prompt = f"""
        You are analyzing news articles for a user who likes: {user_preference}
        
        News Article:
        Title: {news_article.get('title', '')}
        Description: {news_article.get('description', '')}
        
        Based on the user's preference for "{user_preference}", analyze how much they would like this news article.
        
        Provide your response in exactly this format:
        CONFIDENCE: [number 0-100]
        REASON: [explanation why you gave this confidence score]
        
        Example:
        CONFIDENCE: 85
        REASON: This article about meditation directly relates to mental health, which is a core aspect of health and wellness that would interest someone focused on health topics.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking for speed
                ),
            )
            
            response_text = response.text.strip()
            
            # Parse confidence score
            confidence_match = re.search(r'CONFIDENCE:\s*(\d+)', response_text)
            confidence = float(confidence_match.group(1)) if confidence_match else 0.0
            
            # Parse reason
            reason_match = re.search(r'REASON:\s*(.+)', response_text, re.DOTALL)
            reason = reason_match.group(1).strip() if reason_match else "No reason provided"
            
            # Generate confidence message
            if confidence >= 70:
                confidence_msg = "HIGH CONFIDENCE - You'll love this news!"
            elif confidence >= 40:
                confidence_msg = "MEDIUM CONFIDENCE - Might be interesting"
            else:
                confidence_msg = "LOW CONFIDENCE - Probably not your thing"
            
            return {
                "confidence_score": confidence,
                "confidence_message": confidence_msg,
                "reason": reason
            }
            
        except Exception as e:
            print(f"❌ Error analyzing with Gemini: {e}")
            return {
                "confidence_score": 0.0,
                "confidence_message": "LOW CONFIDENCE - Probably not your thing",
                "reason": f"Error occurred: {str(e)}"
            }