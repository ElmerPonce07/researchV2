import os  # Importing the os module for environment variable management
from flask import Flask, request, jsonify, send_from_directory  # Importing necessary Flask components
import openai  # Importing the OpenAI library for API interaction
import requests  # Importing requests library for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for HTML parsing
from dotenv import load_dotenv  # Importing dotenv to load environment variables from a .env file

app = Flask(__name__, static_folder='../frontend', static_url_path='')  # Creating a Flask app instance

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key and SerpAPI key from environment variables
openai.api_key = os.getenv('openai.api.key')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

@app.route('/')  # Defining the route for the home page
def index():
    return send_from_directory(app.static_folder, 'index.html')  # Serve the index.html file from the static folder

@app.route('/search', methods=['POST'])  # Defining a route for search functionality that accepts POST requests
def search():
    keyword = request.json.get('keyword')  # Get the keyword from the request's JSON body

    # Prepare parameters for the SerpAPI request
    params = {
        "q": keyword,  # The search query
        "location": "Austin, TX",  # Set the location for search results
        "api_key": SERPAPI_KEY  # Include the SerpAPI key
    }

    # Call SerpAPI to retrieve search results
    response = requests.get("https://serpapi.com/search", params=params)

    # Check if the response status is not OK (200)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve search results'}), 400  # Return an error message if the request failed

    results = response.json()  # Parse the response JSON into a Python dictionary
    print("SerpAPI response:", results)  # Log the full response for debugging

    # Check if organic_results exists and is not empty
    if 'organic_results' not in results or not results['organic_results']:
        return jsonify({'error': 'No results found'}), 404  # Return an error if no results are found

    # Extract the URLs from the search results
    urls = [result['link'] for result in results['organic_results'] if 'link' in result]

    # Initialize a list for valid URLs
    valid_urls = []
    for url in urls:
        try:
            # Use HEAD request to check if the URL is reachable
            url_response = requests.head(url, timeout=5)
            if url_response.status_code == 200:  # If the URL is reachable
                # Skip specific social media links
                if 'play.google.com' in url or 'snapchat.com' in url or 'facebook.com' in url or 'youtube.com' in url or 'instagram.com' in url:
                    continue  # Skip YouTube and Instagram links

                # Check the Content-Type to ensure it's HTML
                content_type = url_response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    continue  # Skip non-HTML content

                valid_urls.append(url)  # Add the valid URL to the list

        except requests.RequestException:
            # Handle any exceptions (e.g., timeouts, connection errors)
            continue  # Skip to the next URL if there's an error

    return jsonify({'urls': valid_urls})  # Return the list of valid URLs as a JSON response

@app.route('/summarize', methods=['POST'])  # Defining a route for summarizing content that accepts POST requests
def summarize():
    url = request.json.get('url')  # Get the URL from the request's JSON body
    response = requests.get(url)  # Fetch the content from the URL

    # Check if the response status is not OK (200)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve the URL'}), 400  # Return an error message if the request failed

    # Scrape the text content from the URL using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])  # Extract text from all paragraph elements

    # Call OpenAI's GPT model to summarize the scraped content
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model to use
        messages=[  # Prepare the messages for the model
            {"role": "system", "content": "You are a helpful assistant. Always summarize text in a concise manner and provide key points at the end."},
            {"role": "user", "content": f"Summarize the following article: {text}"}
        ]
    )

    # Extract the summary from the OpenAI response
    summary = openai_response['choices'][0]['message']['content']

    return jsonify({'summary': summary})  # Return the summary as a JSON response

@app.route('/translate', methods=['POST'])  # Defining a route for translating text that accepts POST requests
def translate():
    data = request.json  # Get the data from the request's JSON body
    summary = data.get('summary')  # Extract the summary text to be translated
    language = data.get('language')  # Extract the target language for translation

    # Call OpenAI's GPT model to translate the summary
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Specify the model to use
        messages=[  # Prepare the messages for the model
            {"role": "system", "content": f"You are a helpful assistant. Translate the following text to {language}."},
            {"role": "user", "content": summary}
        ]
    )

    # Extract the translated text from the OpenAI response
    translated = openai_response['choices'][0]['message']['content']

    return jsonify({'translated': translated})  # Return the translated text as a JSON response

if __name__ == '__main__':  # Check if this script is run directly
    app.run(debug=True)  # Run the Flask application in debug mode
