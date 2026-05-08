CURRICULUM_TOPICS = {
    "english": [
        {
            "id": "reading_comprehension",
            "label": "Reading comprehension",
            "description": "Answer who, what, where, when, why, and main-idea questions from a short passage.",
        },
        {
            "id": "vocabulary",
            "label": "Vocabulary",
            "description": "Practice word meaning, synonyms, antonyms, and words used in context.",
        },
        {
            "id": "grammar",
            "label": "Grammar",
            "description": "Practice nouns, verbs, adjectives, sentence order, capitalization, and punctuation.",
        },
        {
            "id": "sentence_writing",
            "label": "Sentence writing",
            "description": "Build, complete, or improve simple grade-level sentences.",
        },
    ],
    "sociales_colombia": [
        {
            "id": "colombian_geography",
            "label": "Colombian geography",
            "description": "Practice maps, regions, departments, cities, landforms, rivers, and local places.",
        },
        {
            "id": "colombian_history",
            "label": "Colombian history",
            "description": "Practice age-appropriate Colombian history, symbols, communities, and cultural events.",
        },
        {
            "id": "civic_behavior",
            "label": "Civic behavior and society",
            "description": "Practice respect, rules, responsibility, cooperation, family, school, and community roles.",
        },
    ],
    "math": [
        {
            "id": "addition",
            "label": "Addition",
            "description": "Practice adding numbers with deterministic answer checking.",
        },
        {
            "id": "subtraction",
            "label": "Subtraction",
            "description": "Practice subtracting numbers with deterministic answer checking.",
        },
        {
            "id": "word_problems",
            "label": "Word problems",
            "description": "Practice short real-life addition and subtraction stories.",
        },
    ],
}


def get_topic(subject: str, topic_id: str) -> dict | None:
    for topic in CURRICULUM_TOPICS.get(subject, []):
        if topic["id"] == topic_id:
            return topic

    return None


def get_default_topic_id(subject: str) -> str:
    topics = CURRICULUM_TOPICS.get(subject, [])

    if not topics:
        return "general"

    return topics[0]["id"]
