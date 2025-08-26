"""Simple Weather Agent Pipeline for Serving Demo.

This pipeline uses an AI agent to analyze weather for any city.
It can be deployed and served as a FastAPI endpoint.
"""

import random
from typing import Dict

from zenml import pipeline, step


@step
def get_weather(city: str) -> Dict[str, float]:
    """Simulate getting weather data for a city."""
    # In real life, this would call a weather API
    # For demo, we generate based on city name
    temp_base = sum(ord(c) for c in city.lower()) % 30
    return {
        "temperature": temp_base + random.uniform(-5, 5),
        "humidity": 40 + (ord(city[0]) % 40),
        "wind_speed": 5 + (len(city) % 15),
    }


@step
def analyze_weather_with_llm(weather_data: Dict[str, float], city: str) -> str:
    """Use LLM to analyze weather and provide intelligent recommendations."""
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind = weather_data["wind_speed"]

    # Create a prompt for the LLM
    weather_prompt = f"""You are a weather expert AI assistant. Analyze the following weather data for {city} and provide detailed insights and recommendations.

Weather Data:
- City: {city}
- Temperature: {temp:.1f}°C
- Humidity: {humidity}%
- Wind Speed: {wind:.1f} km/h

Please provide:
1. A brief weather assessment
2. Comfort level rating (1-10)
3. Recommended activities
4. What to wear
5. Any weather warnings or tips

Keep your response concise but informative."""

    try:
        # Try to use OpenAI API if available
        import os

        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ImportError("OpenAI API key not found")

        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful weather analysis expert.",
                },
                {"role": "user", "content": weather_prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        llm_analysis = response.choices[0].message.content

        return f"""🤖 LLM Weather Analysis for {city}:

{llm_analysis}

---
Raw Data: {temp:.1f}°C, {humidity}% humidity, {wind:.1f} km/h wind
Powered by: OpenAI GPT-3.5-turbo"""

    except Exception as e:
        # Fallback to rule-based analysis if LLM fails
        print(f"LLM analysis failed ({e}), using fallback...")

        # Enhanced rule-based analysis
        if temp < 0:
            temp_desc = "freezing"
            comfort = 2
            activities = "indoor activities, ice skating"
            clothing = "heavy winter coat, gloves, warm boots"
            warning = "⚠️ Risk of frostbite - limit outdoor exposure"
        elif temp < 10:
            temp_desc = "cold"
            comfort = 4
            activities = "brisk walks, winter sports"
            clothing = "warm jacket, layers, closed shoes"
            warning = "Bundle up to stay warm"
        elif temp < 25:
            temp_desc = "pleasant"
            comfort = 8
            activities = "hiking, cycling, outdoor dining"
            clothing = "light jacket or sweater"
            warning = "Perfect weather for outdoor activities!"
        elif temp < 35:
            temp_desc = "hot"
            comfort = 6
            activities = "swimming, early morning walks"
            clothing = "light clothing, sun hat, sunscreen"
            warning = "Stay hydrated and seek shade"
        else:
            temp_desc = "extremely hot"
            comfort = 3
            activities = "indoor activities, swimming"
            clothing = "minimal light clothing, sun protection"
            warning = "⚠️ Heat warning - avoid prolonged sun exposure"

        # Humidity adjustments
        if humidity > 80:
            comfort -= 1
            warning += " High humidity will make it feel warmer."
        elif humidity < 30:
            warning += " Low humidity may cause dry skin."

        # Wind adjustments
        if wind > 20:
            warning += " Strong winds - secure loose items."

        return f"""🤖 Weather Analysis for {city}:

Assessment: {temp_desc.title()} weather with {humidity}% humidity
Comfort Level: {comfort}/10
Wind Conditions: {wind:.1f} km/h

Recommended Activities: {activities}
What to Wear: {clothing}
Weather Tips: {warning}

---
Raw Data: {temp:.1f}°C, {humidity}% humidity, {wind:.1f} km/h wind
Analysis: Rule-based AI (LLM unavailable)"""


@pipeline
def weather_agent_pipeline(city: str = "London") -> str:
    """Weather agent pipeline that can be served via API.

    Uses LLM to provide intelligent weather analysis.

    Args:
        city: City name to analyze weather for

    Returns:
        LLM-powered weather analysis and recommendations
    """
    weather_data = get_weather(city=city)
    analysis = analyze_weather_with_llm(weather_data=weather_data, city=city)
    return analysis


if __name__ == "__main__":
    # Create a deployment (not run it!)
    # We need to access the private _create_deployment method because
    # ZenML doesn't have a public method to create deployments without running

    # First prepare the pipeline
    weather_agent_pipeline._prepare_if_possible()

    # Create deployment without running
    deployment = weather_agent_pipeline._create_deployment()

    print("\n✅ Pipeline deployed!")
    print(f"📋 Deployment ID: {deployment.id}")
    print("\n🚀 To serve this pipeline:")
    print(f"   export ZENML_PIPELINE_DEPLOYMENT_ID={deployment.id}")
    print("   python -m zenml.serving")
