from cs50 import SQL
from mlconjug3 import Conjugator
from flask import redirect, render_template, session
from functools import wraps
import re
import random

conjugator = Conjugator()

db = SQL("sqlite:///site.db")


def login_required(f):
    """ Decorate routes to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def validate(password):
    """ Validate password entered."""
    if len(password) < 8:
        return False
    elif re.search('[A-Z]', password) is None:
        return False
    elif re.search('[a-z]', password) is None:
        return False
    elif re.search('[0-9]', password) is None:
        return False
    else:
        return True

def generate_result():
    """Generates conjugation result from list of verbs, moods and tenses to include.
    Returns: 1. verb root, 2. pronoun, 3. mood, 4. tense, 5. conjugated form with pronoun."""

    verb_types = session.get("verb_types")
    verb_list = db.execute("SELECT name FROM verbs WHERE type IN (?) AND (user_id = ? OR user_id IS NULL)",
                           verb_types, session.get('user_id'))
    verb = random.choice(verb_list)['name'].strip()

    # Get included moods
    # FALLOIR FIX
    if verb == 'falloir':
        mood_list = db.execute("SELECT name FROM moods WHERE name IN (?) AND name IS NOT 'Imperatif'", session.get("mood_list"))
    else:
        mood_list = db.execute("SELECT name FROM moods WHERE name IN (?)", session.get("mood_list"))
    mood = random.choice(mood_list)['name'].strip()

    # Generate list of tenses to include
    if mood == 'Indicatif':
        tense_list = db.execute("SELECT name FROM tenses WHERE name IN (?) AND tense_id < 5", session.get("tense_list"))
        tense = random.choice(tense_list)['name'].strip()
    elif mood == 'Conditionnel':
        tense = 'Présent'
    elif mood == 'Subjonctif':
        tense_list = ['Présent', 'Imparfait']
        tense = random.choice(tense_list).strip()
    elif mood == 'Imperatif':
        tense = 'Imperatif Présent'
    elif mood == 'Participe':
        tense_list = ['Participe Présent', 'Participe Passé']
        tense = random.choice(tense_list).strip()

    # Conjugate the verb
    conj_verb = conjugator.conjugate(verb)

    # Get list of pronouns to include
    # FALLOIR FIX
    if verb == 'falloir':
        if mood == 'Participe':
            pronoun = 'masculin singulier'
        else:
            pronoun = 'il (elle, on)'
    else:
        pronoun_list = []
        if tense in ['Participe Présent', 'Infinitif Présent']:
            pronoun_list = None
        else:
            for pronoun, conjugation in conj_verb[mood][tense].items():
                pronoun_list.append(pronoun)

        if not pronoun_list:
            pronoun = None
        else:
            pronoun = random.choice(pronoun_list).strip()

    # Conjugate verb
    if pronoun == None:
        conjugation = conj_verb[mood][tense]
        correct_answer = conjugation
    else:
        conjugation = conj_verb[mood][tense][pronoun]

        # Special condition (make il, elle, on / ils, elles separate choices)
        if pronoun == 'il (elle, on)':
            pronoun = random.choice(['il', 'elle', 'on'])
        if pronoun == 'ils (elles)':
            pronoun = random.choice(['ils', 'elles'])

        # Special condition (for past participles)
        if tense == 'Participe Passé':
            correct_answer = conjugation
        # Special condition (for imperative, which has ''  as the pronoun instead of None)
        elif pronoun == '':
            correct_answer = conjugation
        # Special condition (if conjugated form starts with a vowel, je should become j')
        elif conjugation[0] in ['a', 'e', 'é', 'i', 'o', 'ô', 'u'] and pronoun == 'je':
            correct_answer = 'j\'' + conjugation
        else:
            correct_answer = pronoun + ' ' + conjugation
    return [verb, pronoun, mood, tense, correct_answer]
