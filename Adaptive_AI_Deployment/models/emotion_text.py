from textblob import TextBlob

def detect_text_emotion(text):
    """
    Detect emotion from text using sentiment polarity.
    Returns a list with a 'label' key to match backend usage.
    """

    if not text:
        return [{"label": "Neutral"}]

    polarity = TextBlob(text).sentiment.polarity

    if polarity >= 0.05:
        label = "Positive"
    elif polarity <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return [{"label": label}]
