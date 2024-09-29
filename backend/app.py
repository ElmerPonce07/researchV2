from flask import Flask, request, jsonify, send_from_directory
import openai
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')

openai.api_key =  'sk-LU77YQa2CaldZtSAkmCtdqNYoPimNGJk1ghFQIe6gJT3BlbkFJK50s5w6-Rv4QEdXj6HXh9JH-nC_MXaM3RMswB3DW4A'  # Replace with your OpenAI API key
SERPAPI_KEY = 'b380a2b7bc1a3586d23a9abe919e19ce1421b052b997643c1a011e10a5f6bb65'  # Replace with your SerpAPI key


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/search', methods=['POST'])
def search():
    keyword = request.json.get('keyword')

    # Use requests to make a direct API call to SerpAPI
    params = {
        "q": keyword,
        "location": "Austin, TX",  # Change location if needed
        "api_key": SERPAPI_KEY
    }

    # Call SerpAPI to retrieve search results
    response = requests.get("https://serpapi.com/search", params=params)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve search results'}), 400

    results = response.json()

    # Extract the URLs from the search results
    urls = [result['link'] for result in results['organic_results']]

    return jsonify({'urls': urls})


@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.json.get('url')
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve the URL'}), 400

    # Scrape the text content from the URL
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ' '.join([p.get_text() for p in soup.find_all('p')])

    # Call OpenAI's GPT model to summarize the scraped content
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant. Always summarize text in a concise manner and provide key points at the end."},
            {"role": "user", "content": f"Summarize the following article: {text}"}
        ]
    )

    # Extract the summary from the OpenAI response
    summary = openai_response['choices'][0]['message']['content']

    return jsonify({'summary': summary})


if __name__ == '__main__':
    app.run(debug=True)
