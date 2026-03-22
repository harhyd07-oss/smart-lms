import os
import requests
from google import genai
from dotenv import load_dotenv
import json
# Educational keywords — if query contains any of these
# it is considered a valid study-related search
EDUCATIONAL_KEYWORDS = [
    # Subjects
    'algorithm', 'data structure', 'programming', 'coding', 'computer',
    'science', 'math', 'mathematics', 'physics', 'chemistry', 'biology',
    'history', 'geography', 'economics', 'english', 'language', 'literature',
    'engineering', 'electronics', 'electrical', 'mechanical', 'civil',
    'database', 'networking', 'operating system', 'software', 'hardware',
    'machine learning', 'artificial intelligence', 'deep learning', 'neural',
    'statistics', 'calculus', 'algebra', 'geometry', 'trigonometry',
    'accounting', 'finance', 'management', 'marketing', 'business',
    'psychology', 'sociology', 'philosophy', 'political', 'law',
    'medical', 'anatomy', 'physiology', 'pharmacology', 'nursing',
    'architecture', 'design', 'art', 'music theory',

    # Programming languages and tools
    'python', 'java', 'javascript', 'c++', 'c#', 'html', 'css', 'sql',
    'react', 'angular', 'nodejs', 'flask', 'django', 'spring', 'kotlin',
    'swift', 'rust', 'golang', 'typescript', 'php', 'ruby', 'scala',
    'git', 'docker', 'kubernetes', 'aws', 'azure', 'linux', 'unix',

    # Study-related terms
    'tutorial', 'learn', 'study', 'course', 'lecture', 'lesson',
    'explain', 'introduction', 'basics', 'beginner', 'advanced',
    'concept', 'theory', 'formula', 'equation', 'proof', 'theorem',
    'sort', 'search', 'tree', 'graph', 'array', 'linked list', 'stack',
    'queue', 'hash', 'recursion', 'dynamic programming', 'greedy',
    'binary', 'loop', 'function', 'class', 'object', 'variable',
    'network', 'protocol', 'http', 'api', 'rest', 'web development',
    'cybersecurity', 'encryption', 'compiler', 'interpreter',
    'exam', 'test', 'quiz', 'assignment', 'homework', 'project',
    'chapter', 'unit', 'module', 'semester', 'grade', 'degree',
]

def is_educational_query(query):
    """
    Checks if query is education related using
    whole word matching to avoid false positives.
    e.g. 'start' should not match 'art'
    """
    import re
    query_lower = query.lower().strip()

    for keyword in EDUCATIONAL_KEYWORDS:
        # Use word boundary matching for single words
        # For phrases (containing space), use simple substring match
        if ' ' in keyword:
            if keyword in query_lower:
                return True
        else:
            # Match whole word only
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_lower):
                return True

    return False
load_dotenv()

GEMINI_API_KEY          = os.getenv('GEMINI_API_KEY')
YOUTUBE_API_KEY         = os.getenv('YOUTUBE_API_KEY')
GOOGLE_SEARCH_API_KEY   = os.getenv('GOOGLE_SEARCH_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

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


def rate_all_resources_with_ai(resources, original_query):
    """
    Rates ALL resources in a SINGLE API call instead of
    one call per resource. This uses 90% less quota.
    """
    if not GEMINI_API_KEY or not resources:
        for r in resources:
            r['ai_rating']  = 3.0
            r['ai_summary'] = 'AI rating unavailable.'
        return resources

    # Build a single prompt with all resources
    resources_text = ""
    for i, r in enumerate(resources):
        resources_text += f"""
Resource {i+1}:
- Title: {r['title']}
- Source: {r['source']}
- Type: {r['type']}
- Description: {r['description'][:100]}
"""

    prompt = f"""
You are an educational resource evaluator. Rate these learning resources for the topic: "{original_query}"

{resources_text}

Rate each resource from 1.0 to 5.0 based on:
1. Relevance to "{original_query}"
2. Educational value
3. Source credibility (YouTube, Wikipedia, GeeksForGeeks = high credibility)

Respond ONLY with a JSON array in this exact format:
[
  {{"index": 1, "rating": 4.5, "summary": "one sentence reason"}},
  {{"index": 2, "rating": 3.2, "summary": "one sentence reason"}},
  ...
]
No other text, just the JSON array.
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        text = response.text.strip()

        # Clean up response in case Gemini adds markdown
        text = text.replace('```json', '').replace('```', '').strip()

        ratings = json.loads(text)

        for rating_obj in ratings:
            idx = rating_obj.get('index', 1) - 1
            if 0 <= idx < len(resources):
                resources[idx]['ai_rating']  = round(
                    max(1.0, min(5.0, float(rating_obj.get('rating', 3.0)))), 1
                )
                resources[idx]['ai_summary'] = rating_obj.get('summary', 'Good resource.')

        return resources

    except Exception as e:
        print(f"Gemini batch rating error: {e}")
        for r in resources:
            r['ai_rating']  = 3.0
            r['ai_summary'] = 'Could not rate this resource.'
        return resources


def search_and_rate(query, min_rating=4.0):
    # ── Validate query is educational ──
    if not is_educational_query(query):
        print(f"Non-educational query blocked: {query}")
        return None  # None signals invalid query

    print(f"Searching for: {query}")

    google_results  = search_google(query,  num_results=5)
    youtube_results = search_youtube(query, num_results=5)

    all_results = google_results + youtube_results
    print(f"Found {len(all_results)} results, rating all with ONE AI call...")

    rated_results = rate_all_resources_with_ai(all_results, query)

    high_quality = [
        r for r in rated_results
        if r.get('ai_rating', 0) >= min_rating
    ]

    if not high_quality:
        high_quality = rated_results

    high_quality.sort(key=lambda x: x.get('ai_rating', 0), reverse=True)

    print(f"Returning {len(high_quality)} high quality resources")
    return high_quality