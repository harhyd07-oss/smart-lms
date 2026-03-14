# algorithms/greedy.py
# Greedy Algorithm for recommending the best resources.
#
# DAA Concept: Greedy Approach
# - At each step, pick the locally optimal choice
# - Here: pick resources with the highest combined score
# - Score = weighted combination of rating + popularity
#
# Why Greedy works here:
# We don't need a globally perfect recommendation —
# we just want "good enough, fast." Greedy is ideal for this.

def calculate_resource_score(resource):
    """
    Calculates a score for each resource based on:
    - Rating (weighted 70%) — quality matters most
    - Downloads (weighted 30%) — popularity as secondary signal
    
    Downloads are normalized to 0-5 scale to match rating scale.
    """
    rating    = resource['rating']    if resource['rating']    else 0
    downloads = resource['downloads'] if resource['downloads'] else 0

    # Normalize downloads to a 0-5 scale
    # Assume max downloads = 500 for normalization
    max_downloads = 500
    normalized_downloads = (downloads / max_downloads) * 5

    # Weighted score
    score = (0.7 * rating) + (0.3 * normalized_downloads)
    return round(score, 3)


def greedy_recommend(resources, top_n=3, course_filter=None):
    """
    Greedily selects the top N resources.
    
    Args:
        resources: full list of resource dicts
        top_n: how many to recommend
        course_filter: optionally filter by course name
    
    Returns:
        List of top_n recommended resources
    """

    # Filter by course if specified
    if course_filter:
        resources = [r for r in resources if r['course'] == course_filter]

    # Calculate score for every resource
    scored = []
    for resource in resources:
        score = calculate_resource_score(resource)
        # Create a copy with score added
        resource_with_score = dict(resource)
        resource_with_score['score'] = score
        scored.append(resource_with_score)

    # Greedy step: sort by score and take top N
    # This is the "greedy choice" — always pick the highest scored item
    scored.sort(key=lambda x: x['score'], reverse=True)

    return scored[:top_n]