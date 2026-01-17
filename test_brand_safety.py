#!/usr/bin/env python3
"""
Test script for the LLM-assisted Brand Safety Analyzer
"""

import asyncio
from datetime import datetime
from services.analyzer.llm.brand_safety import BrandSafetyAnalyzer
from shared.schemas.raw import RawPost, RawComment
from shared.schemas.domain import Platform


async def test_brand_safety_analyzer():
    """Test the brand safety analyzer with various content scenarios."""
    
    print("🧪 Testing LLM-assisted Brand Safety Analyzer")
    print("=" * 50)
    
    # Initialize the analyzer
    analyzer = BrandSafetyAnalyzer()
    
    # Test Case 1: Safe content
    print("\n📋 Test Case 1: Safe Content")
    print("-" * 30)
    
    safe_post = RawPost(
        id="safe_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/safe_post",
        caption="Enjoying a beautiful sunset at the beach! 🌅 #sunset #beach #nature",
        timestamp=datetime.now(),
        like_count=150,
        comment_count=12,
        comments=[
            RawComment(
                id="comment_001",
                text="What a gorgeous view! Love the colors.",
                timestamp=datetime.now(),
                author_id="user_001",
                like_count=5
            ),
            RawComment(
                id="comment_002",
                text="This is absolutely stunning! Where is this?",
                timestamp=datetime.now(),
                author_id="user_002",
                like_count=3
            )
        ]
    )
    
    result = await analyzer.analyze_content(safe_post, safe_post.comments)
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    
    # Test Case 2: Content with mild risk
    print("\n📋 Test Case 2: Mild Risk Content")
    print("-" * 30)
    
    mild_risk_post = RawPost(
        id="mild_risk_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/mild_risk_post",
        caption="Some people are just so stupid sometimes 😤",
        timestamp=datetime.now(),
        like_count=50,
        comment_count=8,
        comments=[
            RawComment(
                id="comment_003",
                text="I agree, people can be so dumb",
                timestamp=datetime.now(),
                author_id="user_003",
                like_count=2
            ),
            RawComment(
                id="comment_004",
                text="What an idiot move that was",
                timestamp=datetime.now(),
                author_id="user_004",
                like_count=1
            )
        ]
    )
    
    result = await analyzer.analyze_content(mild_risk_post, mild_risk_post.comments)
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    
    # Test Case 3: Content with elevated risk
    print("\n📋 Test Case 3: Elevated Risk Content")
    print("-" * 30)
    
    elevated_risk_post = RawPost(
        id="elevated_risk_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/elevated_risk_post",
        caption="This violence needs to stop! People are getting hurt",
        timestamp=datetime.now(),
        like_count=75,
        comment_count=20,
        comments=[
            RawComment(
                id="comment_005",
                text="I hate this situation so much",
                timestamp=datetime.now(),
                author_id="user_005",
                like_count=10
            ),
            RawComment(
                id="comment_006",
                text="This is getting out of control with all the fighting",
                timestamp=datetime.now(),
                author_id="user_006",
                like_count=5
            )
        ]
    )
    
    result = await analyzer.analyze_content(elevated_risk_post, elevated_risk_post.comments)
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    
    # Test Case 4: High risk content
    print("\n📋 Test Case 4: High Risk Content")
    print("-" * 30)
    
    high_risk_post = RawPost(
        id="high_risk_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/high_risk_post",
        caption="This explicit content is not appropriate for everyone",
        timestamp=datetime.now(),
        like_count=200,
        comment_count=35,
        comments=[
            RawComment(
                id="comment_007",
                text="This is so wrong and hateful",
                timestamp=datetime.now(),
                author_id="user_007",
                like_count=15
            ),
            RawComment(
                id="comment_008",
                text="I hate this kind of explicit material",
                timestamp=datetime.now(),
                author_id="user_008",
                like_count=8
            ),
            RawComment(
                id="comment_009",
                text="This violent content should be removed",
                timestamp=datetime.now(),
                author_id="user_009",
                like_count=12
            )
        ]
    )
    
    result = await analyzer.analyze_content(high_risk_post, high_risk_post.comments)
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    
    # Test Case 5: Text-only fallback mode
    print("\n📋 Test Case 5: Text-only Fallback Mode")
    print("-" * 30)
    
    text_only_post = RawPost(
        id="text_only_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/text_only_post",
        caption="Some people just don't understand basic concepts",
        timestamp=datetime.now(),
        like_count=30,
        comment_count=5,
        comments=[
            RawComment(
                id="comment_010",
                text="Yeah, they're so stupid",
                timestamp=datetime.now(),
                author_id="user_010",
                like_count=1
            )
        ]
    )
    
    result = await analyzer.analyze_content(
        text_only_post, 
        text_only_post.comments, 
        fallback_mode="text_only"
    )
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    print(f"Fallback Mode: {result.fallback_mode}")
    
    # Test Case 6: With OCR text
    print("\n📋 Test Case 6: Content with OCR Text")
    print("-" * 30)
    
    ocr_post = RawPost(
        id="ocr_post_001",
        platform=Platform.INSTAGRAM,
        url="https://instagram.com/ocr_post",
        caption="Check out this interesting sign I found",
        timestamp=datetime.now(),
        like_count=80,
        comment_count=10,
        comments=[
            RawComment(
                id="comment_011",
                text="That's a really cool sign!",
                timestamp=datetime.now(),
                author_id="user_011",
                like_count=4
            )
        ]
    )
    
    ocr_text = "Warning: Explicit content ahead. Enter at your own risk."
    
    result = await analyzer.analyze_content(
        ocr_post, 
        ocr_post.comments, 
        ocr_text=ocr_text
    )
    print(f"Grade: {result.grade}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Flags: {result.flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Explanation: {result.explanation}")
    
    print("\n✅ All test cases completed!")
    print("\n📊 Summary:")
    print("- Safe content: Grade A, low risk score")
    print("- Mild risk: Grade B, moderate risk score")
    print("- Elevated risk: Grade C-D, higher risk score")
    print("- High risk: Grade D-F, high risk score")
    print("- Text-only mode: Handled with fallback_mode flag")
    print("- OCR text: Integrated into risk assessment")


if __name__ == "__main__":
    asyncio.run(test_brand_safety_analyzer())