import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure NLTK resources are available
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)


class ResumeMatcher:
    def __init__(self, course_description):
        self.course_description = course_description
        self.vectorizer = TfidfVectorizer(stop_words='english')  # Optionally, handle stop words here
        self.lemmatizer = WordNetLemmatizer()
        self.course_vector = self.vectorizer.fit_transform([self.preprocess(course_description)])

    def preprocess(self, text):
        """
        Preprocess the text by tokenizing, removing stopwords (optional here), and lemmatizing.
        """
        tokens = word_tokenize(text.lower())
        cleaned_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
        return ' '.join(cleaned_tokens)

    def compute_match_score(self, resume_text):
        """
        Compute the match score (cosine similarity) between a resume and the course description.
        """
        resume_vector = self.vectorizer.transform([self.preprocess(resume_text)])
        cosine_sim = cosine_similarity(resume_vector, self.course_vector)
        return cosine_sim[0][0]
