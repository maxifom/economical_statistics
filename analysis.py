import pymorphy2
from polyglot.text import Text

morpher = pymorphy2.MorphAnalyzer()


def sentence_info(sentence):
    sentence = sentence.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    sentence = sentence.split(' ')
    for i in range(len(sentence)):
        sentence[i] = morpher.parse(sentence[i])[0].normal_form
    sentence = ' '.join(sentence)
    text = Text(text=sentence, hint_language_code='ru')
    word_count = 0
    for key, c in text.word_counts.items():
        word_count += c
    result = dict()
    result['score'] = text.polarity
    result['count'] = word_count
    return result


def linear_regression(news):
    for n in news:
        info = sentence_info(n['text'])
        sent_score = info['score']
        word_count = info['count']
