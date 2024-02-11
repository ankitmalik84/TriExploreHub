from uagents import Agent, Context, Protocol
from messages import TopDestinations, UAgentResponse, UAgentResponseType, KeyValue
from uagents.setup import fund_agent_if_low
import os
from twilio.rest import Client


# Initialize Twilio client with your credentials
account_sid = 'AC5f05e6270f412821cda29fc4b764d9a0'
auth_token = 'a79cbfc27076ac6109d18ef57d0ffe61'
client = Client(account_sid, auth_token)

def send_whatsapp_notification(phone_number, message):
    try:
        # Send WhatsApp message using Twilio client
        whatsapp_message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to='whatsapp:+918449035579'
        )
        print(f"WhatsApp notification sent to {phone_number}: {whatsapp_message.sid}")
    except Exception as e:
        print(f"Error sending WhatsApp notification: {e}")



# TOP_DESTINATIONS_SEED = os.getenv("TOP_DESTINATIONS_SEED", "top_destinations really secret phrase :)")

agent = Agent(
    name="top_destinations",
    seed= "top_destinations",
)

fund_agent_if_low(agent.wallet.address())

# llm = get_llm()
top_destinations_protocol = Protocol("TopDestinations")

predefined_destinations = {
    "default": [
        KeyValue(key="Goa, India", value="Goa is a popular destination for tourists. It has good weather and beaches."),
        KeyValue(key="Malé, Maldives", value="Maldives is a popular destination for tourists. It has good weather and beaches."),
    ],
    "good_weather_beaches": [
        KeyValue(key="Goa, India", value="Goa is a popular destination for tourists. It has good weather and beaches."),
        KeyValue(key="Malé, Maldives", value="Maldives is a popular destination for tourists. It has good weather and beaches."),
        KeyValue(key="Barcelona, Spain", value="Barcelona has a Mediterranean climate with mild winters and warm summers, perfect for beach lovers."),
        KeyValue(key="Phuket, Thailand", value="Phuket is famous for its stunning beaches, clear waters, and vibrant nightlife."),
        KeyValue(key="Honolulu, Hawaii", value="Honolulu offers beautiful beaches, lush landscapes, and a unique blend of Hawaiian and American cultures."),
    ],
    "cultural_experience": [
        KeyValue(key="Rome, Italy", value="Rome is a city rich in history and culture. Visit the Colosseum, Roman Forum, and Vatican City."),
        KeyValue(key="Paris, France", value="Paris is known as the City of Light and is home to iconic landmarks like the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral."),
        KeyValue(key="Kyoto, Japan", value="Kyoto is famous for its temples, gardens, and traditional tea houses. Explore the historic Gion district and visit the Fushimi Inari Shrine."),
        KeyValue(key="Cairo, Egypt", value="Cairo is home to ancient wonders like the Pyramids of Giza, Sphinx, and Egyptian Museum, offering a glimpse into Egypt's rich history."),
    ],
}

@top_destinations_protocol.on_message(model=TopDestinations, replies=UAgentResponse)
async def get_top_destinations(ctx: Context, sender: str, msg: TopDestinations):
    ctx.logger.info(f"Received message from {sender}, session: {ctx.session}, message data: {msg}")
    
    try:
        preference_mapping = {
            "default": predefined_destinations["default"],
            "good_weather_beaches": predefined_destinations["good_weather_beaches"],
            "cultural_experience": predefined_destinations["cultural_experience"]
        }

        categories = msg.preferences.split(";") if msg.preferences else []
        response = preference_mapping.get(categories[0], predefined_destinations["default"]) if categories else predefined_destinations["default"]
        
        response_strings = [f"{item.key}: {item.value}" for item in response]
        response_dicts = [{"key": idx, "value": item} for idx, item in enumerate(response_strings)]
        response = response_dicts
        send_whatsapp_notification('+918449035579', response_strings)
        await ctx.send(
            sender,
            UAgentResponse(
                options=response,
                type=UAgentResponseType.FINAL_OPTIONS
            )
        )
    except Exception as exc:
        ctx.logger.warn(exc)
        await ctx.send(sender, UAgentResponse(message=str(exc), type=UAgentResponseType.ERROR))


agent.include(top_destinations_protocol)

