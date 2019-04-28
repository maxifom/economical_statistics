import pymorphy2
from misc.database import Database

morpher = pymorphy2.MorphAnalyzer()


def sentence_info(sentence, positive=[], negative=[]):
    if len(positive) == 0 and len(negative) == 0:
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
    splitted = sentence.split('.')
    first_sentence = splitted[0]
    first_sentence = first_sentence.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(
        ' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    first_sentence = first_sentence.split(' ')
    for i in range(len(first_sentence)):
        c = 0
        while first_sentence[i] != morpher.parse(first_sentence[i])[0].normal_form:
            first_sentence[i] = morpher.parse(first_sentence[i])[0].normal_form
            c += 1
            if c > 5:
                break
    sentence = '.'.join(splitted[1:])
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
    result["word_count"] = len(sentence) + len(first_sentence)
    result["sentence"] = ' '.join(first_sentence) + ' ' + ' '.join(sentence)
    positives = 0
    negatives = 0
    # title
    for p in positive:
        words_to_delete = []
        spl = p["word"].split(' ')
        l = len(spl)
        _p = dict()
        for i in range(0, len(first_sentence)):
            tr = True
            for j in range(0, l):
                if i + j < len(first_sentence):
                    if spl[j] != first_sentence[i + j]:
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
                _p["count"] += 10
                positives += 10
        new_sentence = []
        index = 0
        for s in first_sentence:
            if index not in words_to_delete:
                new_sentence.append(first_sentence[index])
            index += 1
        first_sentence = new_sentence
        words_to_delete = []
        if "word" in _p:
            words.append(_p)
    for p in negative:
        words_to_delete = []
        spl = p["word"].split(' ')
        l = len(spl)
        _p = dict()
        for i in range(0, len(first_sentence)):
            tr = True
            for j in range(0, l):
                if i + j < len(first_sentence):
                    if spl[j] != first_sentence[i + j]:
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
                _p["count"] += 10
                negatives += 10
        new_sentence = []
        index = 0
        for s in first_sentence:
            if index not in words_to_delete:
                new_sentence.append(first_sentence[index])
            index += 1
        first_sentence = new_sentence
        words_to_delete = []
        if "word" in _p:
            words.append(_p)

    # Text
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
    if positives + negatives != 0:
        result["sent_score"] = (positives - negatives) / (positives + negatives)
    else:
        result["sent_score"] = 0
    result["words"] = words
    return result


if __name__ == '__main__':
    s = """Чистая прибыль "ФосАгро" в 2018 году снизилась на 13%. Чистая прибыль "ФосАгро" по МСФО в 2018 году снизилась на 13% - до 22,135 млрд рублей, сообщает компания.Выручка составила 233,43 млрд рублей (+29%).Выручка "ФосАгро" за четвертый квартал выросла на 30% до 59,4 млрд рублей (893 млн долларов США), в то время как EBITDA увеличилась на 51% до 18,6 млрд рублей (279 млн долларов США). Таким образом, в четвертом квартале 2018 года рентабельность по EBITDA увеличилась до 31% с 27% годом ранее.Чистая прибыль (скорректированная на неденежные валютные статьи) за четвертый квартал выросла практически в три раза до 10,9 млрд рублей (164 млн долларов США), данный показатель за 2018 год достиг 41,7 млрд рублей (666 млн долларов США)."""
    print(sentence_info(s))
