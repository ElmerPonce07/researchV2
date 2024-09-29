from flask import Flask, request, jsonify, send_from_directory
import openai
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Replace with your OpenAI API key and SerpAPI key
openai.api_key =  'sk-LU77YQa2CaldZtSAkmCtdqNYoPimNGJk1ghFQIe6gJT3BlbkFJK50s5w6-Rv4QEdXj6HXh9JH-nC_MXaM3RMswB3DW4A'

SERPAPI_KEY = 'b380a2b7bc1a3586d23a9abe919e19ce1421b052b997643c1a011e10a5f6bb65'

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
    print("SerpAPI response:", results)  # Log the full response for debugging

    # Check if organic_results exists and is not empty
    if 'organic_results' not in results or not results['organic_results']:
        return jsonify({'error': 'No results found'}), 404

    # Extract the URLs from the search results
    urls = [result['link'] for result in results['organic_results'] if 'link' in result]

    # Filter out links that give a 400 status code or belong to YouTube/Instagram
    valid_urls = []
    for url in urls:
        try:
            url_response = requests.head(url, timeout=5)  # Use HEAD to check if the URL is reachable
            if url_response.status_code == 200:
                # Check if the URL is from YouTube or Instagram
                if 'play.google.com' in url or 'snapchat.com' in url or 'facebook.com' in url or 'youtube.com' in url or 'instagram.com' in url:
                    continue  # Skip YouTube and Instagram links

                # Optionally, check the Content-Type or response content here
                content_type = url_response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    continue  # Skip non-HTML content

                valid_urls.append(url)

        except requests.RequestException:
            # Handle any exceptions (e.g., timeouts, connection errors)
            continue

    return jsonify({'urls': valid_urls})

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
            {"role": "system", "content": "You are a helpful assistant. Always summarize text in a concise manner and provide key points at the end."},
            {"role": "user", "content": f"Summarize the following article: {text}"}
        ]
    )

    # Extract the summary from the OpenAI response
    summary = openai_response['choices'][0]['message']['content']

    return jsonify({'summary': summary})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    summary = data.get('summary')
    language = data.get('language')

    # Call OpenAI's GPT model to translate the summary
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. Translate the following text to {language}."},
            {"role": "user", "content": summary}
        ]
    )

    # Extract the translated text from the OpenAI response
    translated = openai_response['choices'][0]['message']['content']

    return jsonify({'translated': translated})

if __name__ == '__main__':
    app.run(debug=True)

