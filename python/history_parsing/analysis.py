import pymorphy2
from database import Database

morpher = pymorphy2.MorphAnalyzer()


def sentence_info(sentence):
    db = Database()
    db.db.execute("""
        SELECT word from words WHERE is_positive=1
    """)
    positive = db.db.fetchall()
    db.db.execute("""
            SELECT word from words WHERE is_positive=0
        """)
    negative = db.db.fetchall()
    positive = sorted(positive, key=lambda x: len(x["word"].split(' ')), reverse=True)
    negative = sorted(negative, key=lambda x: len(x["word"].split(' ')), reverse=True)
    words = list()
    sentence = sentence.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    sentence = sentence.split(' ')
    for i in range(len(sentence)):
        c = 0
        while sentence[i] != morpher.parse(sentence[i])[0].normal_form:
            sentence[i] = morpher.parse(sentence[i])[0].normal_form
            c += 1
            if c > 5:
                break
    result = dict()
    result["word_count"] = len(sentence)
    result["sentence"] = ' '.join(sentence)
    positives = 0
    negatives = 0
    for p in positive:
        words_to_delete = []
        spl = p["word"].split(' ')
        l = len(spl)
        _p = dict()
        for i in range(0, len(sentence)):
            tr = True
            for j in range(0, l):
                if i + j < len(sentence):
                    if spl[j] != sentence[i + j]:
                        tr = False
                        break
                    else:
                        words_to_delete.append(i + j)
                        tr = True
                else:
                    tr = False
                    break
            if tr:
                _p["word"] = p["word"]
                _p["score"] = 1
                if "count" not in _p:
                    _p["count"] = 0
                _p["count"] += 1
                positives += 1
        new_sentence = []
        index = 0
        for s in sentence:
            if index not in words_to_delete:
                new_sentence.append(sentence[index])
            index += 1
        sentence = new_sentence
        words_to_delete = []
        if "word" in _p:
            words.append(_p)
    for p in negative:
        words_to_delete = []
        spl = p["word"].split(' ')
        l = len(spl)
        _p = dict()
        for i in range(0, len(sentence)):
            tr = True
            for j in range(0, l):
                if i + j < len(sentence):
                    if spl[j] != sentence[i + j]:
                        tr = False
                        break
                    else:
                        words_to_delete.append(i + j)
                        tr = True
                else:
                    tr = False
                    break
            if tr:
                _p["word"] = p["word"]
                _p["score"] = -1
                if "count" not in _p:
                    _p["count"] = 0
                _p["count"] += 1
                negatives += 1
        new_sentence = []
        index = 0
        for s in sentence:
            if index not in words_to_delete:
                new_sentence.append(sentence[index])
            index += 1
        sentence = new_sentence
        words_to_delete = []
        if "word" in _p:
            words.append(_p)
    if positives - negatives != 0:
        result["sent_score"] = (positives - negatives) / (positives + negatives)
    else:
        result["sent_score"] = 0
    result["words"] = words
    return result


if __name__ == '__main__':
    s = """Прибыль "Мечела" за 2018 год выросла на 9%. Прибыль "Мечела", приходящаяся на акционеров, составила в 2018 году по МСФО 12,6 млрд рублей, увеличившись на 9%, сообщила компания. Консолидированная выручка увеличилась на 5% г/г – до 312,6 млрд рублей. Показатель EBITDA снизился на 7% г/г - до 75,7 млрд рублей."""
    print(sentence_info(s))
