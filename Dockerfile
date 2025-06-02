# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# This includes bot.py
COPY bot.py /app/

# Install any needed packages specified in requirements.txt
# Create a dummy requirements.txt if not provided, or install directly
# For this simple case, install pyrogram directly
RUN pip install pyrogram

# Make port 80 available to the world outside this container
# Telegram bots don't typically use ports for incoming connections unless webhooks are used.
# This line is usually not needed for long-polling bots.
# EXPOSE 80

# Run bot.py when the container launches
# It's recommended to pass secrets like API_ID, API_HASH, BOT_TOKEN
# as environment variables when running the container, rather than hardcoding them or
# adding them to the Dockerfile or checked-in code.
# The current bot.py hardcodes these, ideally you'd modify it to read from env vars.
CMD ["python", "bot.py"]
