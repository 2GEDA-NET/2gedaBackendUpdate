# suggestions.py (create a new Python file for your suggestions logic)

from poll.utils import calculate_similarity
from user.utils import get_frequently_searched_polls
from .models import Poll


def suggest_polls(user, all_polls, num_suggestions=5):
    frequently_searched_polls = get_frequently_searched_polls(user)
    similarity_scores = calculate_similarity(frequently_searched_polls, all_polls)

    # Sort polls by similarity scores (descending order)
    ranked_polls_indices = (-similarity_scores).argsort(axis=1)

    # Get the top-ranked polls as suggestions (excluding the user's frequent searches)
    suggested_polls = []

    for i in range(len(frequently_searched_polls)):
        for j in range(1, num_suggestions + 1):
            suggested_poll_index = ranked_polls_indices[i, j]
            suggested_poll = all_polls[suggested_poll_index]

            # Exclude polls that the user has already frequently searched
            if suggested_poll not in suggested_polls and suggested_poll not in frequently_searched_polls:
                suggested_polls.append(suggested_poll)

                # Stop suggesting when reaching the desired number of suggestions
                if len(suggested_polls) == num_suggestions:
                    break

    return suggested_polls
