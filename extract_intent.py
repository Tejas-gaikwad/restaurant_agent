from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
from booking_schemas import BookingIntent

load_dotenv()

client = OpenAI()
MODEL = "gpt-4o-mini"


def extract_intent(user_message, known: dict) -> BookingIntent:
    completion = client.beta.chat.completions.parse(   # or client.chat.completions.parse on newer SDKs
        model=MODEL,
        messages=[
            {"role": "system", "content":
                f"Today is {date.today().isoformat()}. Extract the guest's booking intent "
                f"from their message. Resolve relative dates ('tomorrow') to YYYY-MM-DD. "
                f"Leave a field null if not provided. Never invent a name. "
                f"Already known so far: {known}"},
            {"role": "user", "content": user_message},
        ],
        response_format=BookingIntent,
    )
    return completion.choices[0].message.parsed