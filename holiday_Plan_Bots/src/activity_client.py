from messages import TopActivities, UAgentResponse
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

top_activities_client = Agent(
    name="top_activities_client",
    port=8008,
    seed="client",
    endpoint=["http://127.0.0.1:8008/submit"],
)
fund_agent_if_low(top_activities_client.wallet.address())

preferred_activities_mapping = {
    "0": None,
    "1": "museums",
    "2": "parks",
    "3": "historical_sites",
    # Add more mappings as needed
}

city = input("Enter the city: ") 
date = input("Enter the date (YYYY-MM-DD): ")
preferred_activities = input("Enter your preferred activities (0 for none, 1 for museums, 2 for parks, 3 for historical_sites etc.): ")

preferred_activities_str = preferred_activities_mapping.get(preferred_activities)
top_activities_request = TopActivities(city=city, date=date, preferred_activities=preferred_activities_str)

@top_activities_client.on_interval(period=1000.0)
async def send_message(ctx: Context):
    await ctx.send("agent1qd4jkc3tghpezg4cjattlutn3q5hmk0q35yrxr6e6haseu5cuz3qvh807vp", top_activities_request)
    ctx.logger.info(f"Sent top activities request: {top_activities_request}")

@top_activities_client.on_message(model=UAgentResponse)
async def message_handler(ctx: Context, _: str, msg: UAgentResponse):
    ctx.logger.info("Received top activities options:")
    for item in msg.options:
        ctx.logger.info(f"Activity: {item.key}, Description: {item.value}")

if __name__ == "__main__":
    top_activities_client.run()
