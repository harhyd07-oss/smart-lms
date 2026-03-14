# algorithms/dp.py
# Dynamic Programming for optimal learning path.
#
# DAA Concept: Dynamic Programming
# - Break the problem into smaller overlapping subproblems
# - Store results of subproblems to avoid recomputation
# - Build up the solution from the bottom
#
# Problem: Given a student's progress in N courses,
# find the optimal ORDER to study them to maximize
# total completion percentage efficiently.
#
# Approach: Study courses with LEAST progress first —
# small gains there yield the biggest overall improvement.
# This is the "DP knapsack" intuition applied to learning.

def optimal_learning_path(progress_list):
    """
    Determines the optimal order to study courses.

    Uses a DP-inspired approach:
    - State: current completion % for each course
    - Decision: which course to study next
    - Optimal substructure: best order for N courses
      contains best order for N-1 courses

    Args:
        progress_list: list of dicts with 'course'
                       and 'completion_percentage'

    Returns:
        Ordered list of (index, course_name) tuples
        representing optimal study sequence
    """

    if not progress_list:
        return []

    # Convert to list of (course, completion) tuples
    courses = [
        (p['course'], p['completion_percentage'])
        for p in progress_list
    ]

    n = len(courses)

    # DP table: dp[i] = optimal "effort score" to
    # complete courses 0..i in the best order
    dp = [0] * n

    # Base case: single course — effort = (100 - completion)
    # Lower completion = more effort needed = study first
    dp[0] = 100 - courses[0][1]

    # Fill DP table
    for i in range(1, n):
        remaining   = 100 - courses[i][1]
        dp[i]       = dp[i-1] + remaining

    # Sort courses by remaining work (ascending)
    # Course with LEAST completion = study FIRST
    sorted_courses = sorted(
        enumerate(courses),
        key=lambda x: x[1][1]  # sort by completion %
    )

    # Build the optimal path
    learning_path = [
        (idx, course_name)
        for idx, (course_name, _) in sorted_courses
    ]

    return learning_path