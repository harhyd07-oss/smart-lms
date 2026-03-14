# algorithms/similarity.py
# Cosine Similarity for finding similar resources.
#
# DAA Concept: Vector Space Model
# Each resource is represented as a vector of features.
# Cosine similarity measures the angle between two vectors.
# Smaller angle = more similar resources.
#
# Formula: similarity = (A · B) / (|A| × |B|)
# where A · B is the dot product and |A|, |B| are magnitudes.

import math

def build_feature_vector(resource, all_courses, all_types, all_difficulties):
    """
    Converts a resource dict into a numerical vector.
    This is needed because cosine similarity works on numbers.

    Vector structure:
    [course_encoding, type_encoding, difficulty_encoding, rating, normalized_downloads]
    """
    # Encode course as a number
    course_map = {c: i for i, c in enumerate(all_courses)}
    type_map   = {t: i for i, t in enumerate(all_types)}
    diff_map   = {'Easy': 1, 'Medium': 2, 'Hard': 3}

    course_val     = course_map.get(resource.get('course', ''), 0)
    type_val       = type_map.get(resource.get('type', ''), 0)
    diff_val       = diff_map.get(resource.get('difficulty', ''), 0)
    rating         = resource.get('rating', 0) or 0
    downloads      = resource.get('downloads', 0) or 0
    norm_downloads = min(downloads / 500, 1.0)

    return [course_val, type_val, diff_val, rating, norm_downloads]


def dot_product(vec_a, vec_b):
    """Calculates dot product of two vectors."""
    return sum(a * b for a, b in zip(vec_a, vec_b))


def magnitude(vec):
    """Calculates magnitude (length) of a vector."""
    return math.sqrt(sum(x ** 2 for x in vec))


def cosine_similarity(vec_a, vec_b):
    """
    Calculates cosine similarity between two vectors.
    Returns a value between 0 (different) and 1 (identical).
    """
    mag_a = magnitude(vec_a)
    mag_b = magnitude(vec_b)

    # Avoid division by zero
    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product(vec_a, vec_b) / (mag_a * mag_b)


def find_similar_resources(target_resource, all_resources, top_n=4):
    """
    Finds similar resources based on same subject only.

    Logic:
    1. Filter resources to same subject only
    2. Include ALL resources in that subject (including the clicked one)
    3. Sort by rating — highest first
    4. Return up to 4, never fill with other subjects
    """

    same_subject = []

    for resource in all_resources:
        # Include ALL resources from the same subject
        # including the target resource itself
        if resource.get('course') == target_resource.get('course'):
            same_subject.append(dict(resource))

    # Sort by rating — highest rated first
    same_subject.sort(key=lambda x: x.get('rating') or 0, reverse=True)

    # Return up to 4 — if less than 4 exist, return whatever is available
    return same_subject[:top_n]