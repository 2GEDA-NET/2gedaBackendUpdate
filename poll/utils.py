from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from user.models import Notification

def calculate_similarity(frequently_searched_polls, all_polls):
    # Extract the text (e.g., question) from frequently searched polls
    frequently_searched_text = [poll.question for poll in frequently_searched_polls]

    # Extract the text from all polls
    all_polls_text = [poll.question for poll in all_polls]

    # Create a TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Transform the text into TF-IDF vectors
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_polls_text + frequently_searched_text)

    # Calculate cosine similarity between frequently searched polls and all polls
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Get the similarity scores for frequently searched polls
    frequently_searched_similarity_scores = similarity_matrix[-len(frequently_searched_polls):]

    return frequently_searched_similarity_scores


def create_notification(sender, recipient, message):
    notification = Notification(sender=sender, recipient=recipient, message=message)
    notification.save()