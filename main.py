from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import os
from dotenv import load_dotenv
from database.connection import connect_db, disconnect_db
from database.models import NewsAnalysisModel
from services.news_service import NewsService
from services.gemini_service import GeminiService

load_dotenv()

# Initialize services
news_service = NewsService()
gemini_service = GeminiService()
db_model = NewsAnalysisModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    print("🚀 FastAPI application started")
    
    # Wait a bit for server to fully start, then run analysis
    await asyncio.sleep(2)
    
    
    yield
    
    # Shutdown
    await disconnect_db()
    print("🛑 FastAPI application stopped")

app = FastAPI(title="News Analysis Agent", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "News Analysis Agent is running!"}

@app.post("/analyze-news")
async def analyze_news():
    """Main function to fetch news and analyze user preference"""
    
    user_preference = os.getenv("USER_PREFERENCE")
    print(f"🔍 Analyzing news for user preference: {user_preference}")
    
    # Fetch news
    articles = news_service.get_random_news(count=3)
    
    if not articles:
        return {"error": "No articles found"}
    
    print(f"✅ Found {len(articles)} articles")
    
    # Analyze each article
    await db_model.connect()
    analysis_results = []

    for i, article in enumerate(articles, 1):
        print(f"\n--- Article {i} --")
        print(f"📰 Title: {article['title'][:60]}...")
        
        # Get analysis from Gemini
        analysis = gemini_service.analyze_news_preference(article, user_preference)
        
        # Create result object
        result = {
            "news_title": article['title'],
            "user_preference": user_preference,
            "confidence_score": analysis['confidence_score'],
            "why_this_confidence": analysis['reason']
        }
        
        analysis_results.append(result)
        
        # Console output
        print(f"🤖 AI Confidence: {analysis['confidence_score']}%")
        print(f"📝 {analysis['confidence_message']}")
        print(f"💡 Reason: {analysis['reason']}")
        print(f"🔗 URL: {article['url']}")
        
        # Save to database
        try:
            await db_model.create_analysis(
                title=article['title'],
                description=article.get('description', ''),
                url=article['url'],
                confidence=analysis['confidence_score'],
                preference=user_preference
            )
        except Exception as e:
            print(f"❌ Database error: {e}")
    
    await db_model.disconnect()
    
    # Console output summary
    print("\n" + "="*80)
    print("📊 ANALYSIS SUMMARY")
    print("="*80)
    for i, result in enumerate(analysis_results, 1):
        print(f"Article {i}:")
        print(f"  Title: {result['news_title']}")
        print(f"  User Preference: {result['user_preference']}")
        print(f"  Confidence: {result['confidence_score']}%")
        print(f"  Reason: {result['why_this_confidence']}")
        print("-" * 40)
    
    return {
        "total_articles": len(articles),
        "user_preference": user_preference,
        "analysis_results": analysis_results
    }

