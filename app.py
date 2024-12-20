from flask import Flask, render_template, request
from pyngrok import ngrok
import requests
from transformers import pipeline

app = Flask(__name__)

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

# Apify Dataset API URL
API_URL = "https://api.apify.com/v2/datasets/3lxGtOz3Xfnw5AEe1/items?token=apify_api_z79mrEBZZixIyFSR5PE1iA1yLkLC6Z1yR0K4"

def fetch_news(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data
        except ValueError:
            return []
    return []

def summarize_text(text):
    if len(text) > 1024:
        text = text[:1024]
    elif len(text) == 0:
        return "No summary available."

    try:
        summary = summarizer(text, max_length=250, min_length=100, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return "Summary generation failed due to an error."

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    articles = fetch_news(API_URL)
    articles_data = []

    if articles:
        start = (page - 1) * 5
        end = start + 5
        for article in articles[start:end]:
            url = article.get('url', 'No URL')
            title = article.get('title', 'No Title')
            date = article.get('date', 'No Date')
            authors = article.get('author', [])
            author_names = ', '.join([author.split('/')[-1] for author in authors]) if authors else 'No Author'
            image_url = article.get('image', 'No Image')
            text = article.get('text', '')
            summary = summarize_text(text)

            articles_data.append({
                'url': url,
                'title': title,
                'date': date,
                'author': author_names,
                'image': image_url,
                'summary': summary,
                'full_text': text  # Send the full text for the detailed view
            })

    return render_template('index.html', articles=articles_data, page=page)

@app.route('/article/<int:id>')
def article(id):
    articles = fetch_news(API_URL)
    article = articles[id]
    return render_template('article.html', article=article)

if __name__ == "__main__":
    ngrok.set_auth_token("2ip17ZpWGlJpSJ6WGFTqgfBAY2D_7Z46RPb93VJxnviBHZaKC")
    public_url = ngrok.connect(5000)
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")
    app.run()
