import os
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY          = os.getenv('GEMINI_API_KEY')
YOUTUBE_API_KEY         = os.getenv('YOUTUBE_API_KEY')
GOOGLE_SEARCH_API_KEY   = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def search_google(query, num_results=5):
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_ENGINE_ID:
        return []

    url    = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_SEARCH_API_KEY,
        'cx':  GOOGLE_SEARCH_ENGINE_ID,
        'q':   query + ' tutorial learn',
        'num': num_results,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data     = response.json()
        results  = []

        for item in data.get('items', []):
            results.append({
                'title':       item.get('title', ''),
                'url':         item.get('link', ''),
                'description': item.get('snippet', ''),
                'source':      item.get('displayLink', ''),
                'type':        'article',
                'thumbnail':   None,
                'channel':     None,
            })
        return results

    except Exception as e:
        print(f"Google Search error: {e}")
        return []


def search_youtube(query, num_results=5):
    if not YOUTUBE_API_KEY:
        return []

    url    = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key':               YOUTUBE_API_KEY,
        'q':                 query + ' tutorial',
        'part':              'snippet',
        'type':              'video',
        'maxResults':        num_results,
        'relevanceLanguage': 'en',
        'videoEmbeddable':   'true',
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data     = response.json()
        results  = []

        for item in data.get('items', []):
            snippet  = item.get('snippet', {})
            video_id = item.get('id', {}).get('videoId', '')

            results.append({
                'title':       snippet.get('title', ''),
                'url':         f'https://www.youtube.com/watch?v={video_id}',
                'description': snippet.get('description', '')[:200],
                'source':      'youtube.com',
                'type':        'video',
                'thumbnail':   snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                'channel':     snippet.get('channelTitle', ''),
            })
        return results

    except Exception as e:
        print(f"YouTube Search error: {e}")
        return []


def rate_resource_with_ai(resource, original_query):
    if not GEMINI_API_KEY:
        resource['ai_rating']  = 3.0
        resource['ai_summary'] = 'AI rating unavailable.'
        return resource

    prompt = f"""
You are an educational resource evaluator. Rate this learning resource for the topic: "{original_query}"

Resource details:
- Title: {resource['title']}
- URL: {resource['url']}
- Description: {resource['description']}
- Source: {resource['source']}
- Type: {resource['type']}

Rate this resource from 1 to 5 based on:
1. Relevance to the topic "{original_query}"
2. Educational value and content quality
3. Source credibility (YouTube, Wikipedia, GeeksForGeeks, official docs = high credibility)
4. Clarity of the title and description

Respond in this EXACT format and nothing else:
RATING: [number between 1.0 and 5.0]
SUMMARY: [one sentence explaining why this rating]
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        text = response.text.strip()

        rating  = 3.0
        summary = 'Good resource.'

        for line in text.split('\n'):
            if line.startswith('RATING:'):
                try:
                    rating = float(line.replace('RATING:', '').strip())
                    rating = max(1.0, min(5.0, rating))
                except:
                    rating = 3.0
            elif line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()

        resource['ai_rating']  = round(rating, 1)
        resource['ai_summary'] = summary
        return resource

    except Exception as e:
        print(f"Gemini rating error: {e}")
        resource['ai_rating']  = 3.0
        resource['ai_summary'] = 'Could not rate this resource.'
        return resource


def search_and_rate(query, min_rating=4.0):
    print(f"Searching for: {query}")

    google_results  = search_google(query,  num_results=5)
    youtube_results = search_youtube(query, num_results=5)

    all_results = google_results + youtube_results
    print(f"Found {len(all_results)} results, rating with AI...")

    rated_results = []
    for resource in all_results:
        rated = rate_resource_with_ai(resource, query)
        rated_results.append(rated)

    high_quality = [
        r for r in rated_results
        if r.get('ai_rating', 0) >= min_rating
    ]

    high_quality.sort(key=lambda x: x.get('ai_rating', 0), reverse=True)

    print(f"Returning {len(high_quality)} high quality resources")
    return high_quality