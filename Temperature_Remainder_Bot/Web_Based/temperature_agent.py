from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import requests
from twilio.rest import Client

class Message(Model):
    message: str

# Initialize Twilio client with your credentials
account_sid = 'AC5f05e6270f412821cda29fc4b764d9a0'
auth_token = 'a79cbfc27076ac6109d18ef57d0ffe61'
client = Client(account_sid, auth_token)

# Initialize the temperature agent
temperature_agent = Agent(
    name="temperature_agent",
    port=8000,
    seed="temperature_secret_phrase",
    endpoint=["http://127.0.0.1:8000/submit"],
)
fund_agent_if_low(temperature_agent.wallet.address())

# Define a dictionary to store temperature data for multiple cities
city_temperatures = {}

# Ask the user how many cities they want to track
num_cities = 1
# Function to send WhatsApp notification
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

# Function to trigger notification with temperature, clothing recommendations, and weather poem
def trigger_notification(city_name, city_data):
    current_temperature = city_data['current_temperature']
    desired_min_temp = city_data['desired_min_temp']
    desired_max_temp = city_data['desired_max_temp']
    weather_condition = city_data['weather_condition']

    # Define the message content
    message = f"Temperature in {city_name} is {current_temperature}°C.\n\n Weather: {weather_condition}\n\n"

    if current_temperature < desired_min_temp:
        message += f"Alert: Temperature is below the desired minimum ({desired_min_temp}°C).\n"
    elif current_temperature > desired_max_temp:
        message += f"Alert: Temperature is above the desired maximum ({desired_max_temp}°C).\n"


    # Add clothing recommendations
    clothing_recommendations = generate_clothing_recommendation(city_data)
    message += "Clothing Recommendations:\n" + '\n'.join(clothing_recommendations) + '\n\n'

    # Add weather poem
    weather_poem = generate_weather_poem(city_data)
    message += "Weather Poem:\n" + weather_poem

    # Send WhatsApp notification
    send_whatsapp_notification('+918449035579', message)

# Function to monitor temperature and trigger notifications
def monitor_temperature(city_name, city_data):
    current_temperature = city_data['current_temperature']
    desired_min_temp = city_data['desired_min_temp']
    desired_max_temp = city_data['desired_max_temp']

    if current_temperature is not None:
        if current_temperature < desired_min_temp:
            trigger_notification(city_name, city_data)
            return f"Temperature in {city_name} is below the desired minimum ({desired_min_temp}°C)."
        elif current_temperature > desired_max_temp:
            trigger_notification(city_name, city_data)
            return f"Temperature in {city_name} is above the desired maximum ({desired_max_temp}°C)."
        else:
            trigger_notification(city_name, city_data)
            return f"Temperature in {city_name} is within the desired range ({desired_min_temp}-{desired_max_temp}°C)."
    else:
        return f"Unable to fetch current temperature for {city_name}."
# Function to generate weather poem based on temperature
def generate_weather_poem(city_data):
    current_temperature = city_data['current_temperature']
    weather_condition = city_data['weather_condition']

    poem = ""

    if 'rain' in weather_condition:
        poem = "Raindrops fall from the gray sky,\nPattering softly, my, oh my.\nGrab an umbrella, stay dry and warm,\nNature's music, a soothing charm."
    elif current_temperature < 25:
        poem = "The air is crisp, a chilly embrace,\nA scarf and coat, it's a cool day's grace.\nEmbrace the chill, it's time to play,\nIn cozy layers, you'll keep the cold at bay."
    elif 25 <= current_temperature < 40:
        poem = "The sun is shining bright and high,\nA perfect day to reach the sky.\nGrab your shades and step outside,\nLet the warmth be your guide."
    else:
        poem = "It's a pleasant day, not too hot nor cold,\nEnjoy the weather, let your spirit unfold.\nDress just right and step out the door,\nThe world awaits, there's so much to explore."

    return poem
# Function to generate clothing recommendations based on temperature
def generate_clothing_recommendation(city_data):
    current_temperature = city_data['current_temperature']
    recommendations = []

    if current_temperature < 10:
        recommendations.append("It's very cold. Wear a heavy coat, gloves, and a warm hat.")
    elif 10 <= current_temperature < 20:
        recommendations.append("It's cool. Consider wearing a sweater or jacket.")
    elif 20 <= current_temperature < 30:
        recommendations.append("It's pleasant. Wear light clothing.")
    else:
        recommendations.append("It's hot. Wear light and breathable clothing.")

    return recommendations

# Function to notify the user agent with a message
async def notify_user(ctx: Context, message):
    # Define the user's address (replace with the actual user's address)
    user_address = "agent1qv4ypgs0rswcl4q6t39jxu03zlmk80ru2720ezcssl2jdyx84s0ev4xxms9"

    # Create a message object with a valid model schema
    message_obj = Message(message=message)

    # Send the message to the user agent
    await ctx.send(user_address, message_obj)

# Set start_monitoring_flag to True at the beginning
start_monitoring_flag = False

# Function to start monitoring temperature
def send_user_input_to_temperature_agent(city, min_temp, max_temp):
    # Create a message object with user input
    print("IP ")
    user_input = {
        'city': city,
        'min_temp': min_temp,
        'max_temp': max_temp
    }

    # Send user input to the temperature agent
    # notify_user(user_input)

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=d1845658f92b31c64bd94f06f7188c9c'
    try:
        response = requests.get(url)
        # Initialize temperature_celsius with a default value
        temperature_celsius = None
        weather_condition = None
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Extract and print relevant weather information
            temperature_kelvin = data['main']['temp']
            temperature_celsius = temperature_kelvin - 273.15

            # Extract weather condition
            weather_condition = data['weather'][0]['description']
             # Display current temperature
            print(f"Current temperature in {city}: {temperature_celsius}°C")

        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    
     # Store temperature data in the dictionary
    city_temperatures[city] = {
        'desired_min_temp': min_temp,
        'desired_max_temp': max_temp,
        'current_temperature': temperature_celsius,
        'weather_condition': weather_condition
    }
    for city, city_data in city_temperatures.items():
            temperature_status = monitor_temperature(city, city_data)
            clothing_recommendations = generate_clothing_recommendation(city_data)
            weather_poem = generate_weather_poem(city_data)

@temperature_agent.on_interval(period=3.0)  # Check every 20 seconds
async def temperature_monitor(ctx: Context):
    global start_monitoring_flag
    start_monitoring_flag = True

    if not start_monitoring_flag:
        return

    for city, city_data in city_temperatures.items():
        temperature_status = monitor_temperature(city, city_data)
        clothing_recommendations = generate_clothing_recommendation(city_data)
        weather_poem = generate_weather_poem(city_data)

        ctx.logger.info(temperature_status)

        ctx.logger.info("Clothing Recommendations:")
        for recommendation in clothing_recommendations:
            ctx.logger.info(recommendation)

        ctx.logger.info("Weather Poem:")
        ctx.logger.info(weather_poem)
        await notify_user(ctx, f"{temperature_status}")

if __name__ == "__main__":
    temperature_agent.run()
