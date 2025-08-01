from prisma import Prisma
from typing import Optional

class NewsAnalysisModel:
    def __init__(self):
        self.prisma = Prisma()
    
    async def connect(self):
        await self.prisma.connect()
    
    async def disconnect(self):
        await self.prisma.disconnect()
    
    async def create_analysis(self, title: str, description: str, url: str, confidence: float, preference: str):
        return await self.prisma.newsanalysis.create({
            'title': title,
            'description': description,
            'url': url,
            'confidence': confidence,
            'preference': preference
        })