# algorithms/sorting.py
# Merge Sort implementation for sorting LMS resources.
#
# DAA Concept: Divide and Conquer
# - Divide: split the list into two halves
# - Conquer: recursively sort each half
# - Combine: merge the two sorted halves
#
# Time Complexity:  O(n log n) — always, best/worst/average
# Space Complexity: O(n) — needs extra space for merging

def merge_sort(resources, key='rating', reverse=True):
    """
    Sorts a list of resource dictionaries by a given key.
    
    Args:
        resources: list of resource dicts (from database)
        key: which field to sort by ('rating', 'downloads', etc.)
        reverse: True = descending (highest first), False = ascending
    
    Returns:
        Sorted list of resources
    """

    # BASE CASE: a list of 0 or 1 items is already sorted
    if len(resources) <= 1:
        return resources

    # DIVIDE: find the middle point and split
    mid = len(resources) // 2
    left_half  = resources[:mid]
    right_half = resources[mid:]

    # CONQUER: recursively sort each half
    # Each call reduces the problem size by half
    left_sorted  = merge_sort(left_half,  key, reverse)
    right_sorted = merge_sort(right_half, key, reverse)

    # COMBINE: merge the two sorted halves
    return merge(left_sorted, right_sorted, key, reverse)


def merge(left, right, key, reverse):
    """
    Merges two sorted lists into one sorted list.
    Compares elements one by one and picks the smaller/larger.
    """
    result = []
    i = 0  # pointer for left list
    j = 0  # pointer for right list

    # Compare elements from both lists and add the correct one
    while i < len(left) and j < len(right):

        left_val  = left[i][key]  if left[i][key]  is not None else 0
        right_val = right[j][key] if right[j][key] is not None else 0

        if reverse:
            # Descending: pick the LARGER value first
            if left_val >= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            # Ascending: pick the SMALLER value first
            if left_val <= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    # Add any remaining elements from either list
    # (one list may be longer than the other)
    result.extend(left[i:])
    result.extend(right[j:])

    return result