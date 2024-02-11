from messages import TopDestinations, UAgentResponse
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

top_dest_client = Agent(
    name="top_destinations_client", 
    port=8008,
    seed="client",
    endpoint=["http://127.0.0.1:8008/submit"],
)
fund_agent_if_low(top_dest_client.wallet.address())

preference_mapping = {
    "0": "default",
    "1": "good_weather_beaches",
    "2": "cultural_experience"
}

preference = input("Enter your preference (0 for default, 1 for good weather beaches, 2 for cultural experience): ")
if preference in preference_mapping:
    top_dest_request = TopDestinations(preferences=preference_mapping[preference])
else:
    top_dest_request = TopDestinations(preferences="default")  # Default to "default" if input is invalid

@top_dest_client.on_interval(period=5000.0)
async def send_message(ctx: Context):
    await ctx.send("agent1qdjg53m8ajlg2k9ell49fyxe7t3ucvyezer9uptdyzygfdpr8jdyzlt8axc", top_dest_request)
    ctx.logger.info(f"Sent top destination request: {top_dest_request}")

@top_dest_client.on_message(model=UAgentResponse) 
async def message_handler(ctx: Context, _: str, msg: UAgentResponse):
    ctx.logger.info("Received top destination options:")
    for item in msg.options:
        ctx.logger.info(f"Key: {item.key}, Value: {item.value}")

if __name__ == "__main__":
    top_dest_client.run()
