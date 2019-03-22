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
    splitted = sentence.split('.')
    first_sentence = splitted[0]
    first_sentence = first_sentence.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    first_sentence = first_sentence.split(' ')
    for i in range(len(first_sentence)):
        c = 0
        while first_sentence[i] != morpher.parse(first_sentence[i])[0].normal_form:
            first_sentence[i] = morpher.parse(first_sentence[i])[0].normal_form
            c += 1
            if c > 5:
                break
    print(first_sentence)
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
    result["sentence"] = ' '.join(first_sentence) + ' '.join(sentence)
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
    if positives - negatives != 0:
        result["sent_score"] = (positives - negatives) / (positives + negatives)
    else:
        result["sent_score"] = 0
    result["words"] = words
    return result


if __name__ == '__main__':
    s = """Инвестпрограмма "Роснефти" в 2017 году составит 1,1 трлн рублей, в 2018 - 1,3 трлн. "Роснефть" планирует направить на инвестиционную программу "Роснефти" в 2017 году 1,1 трлн рублей, в 2018 году – 1,3 трлн. Об этом рассказал глава компании Игорь Сечин на встрече с Владимиром Путиным.В 2017 году компания придаст особое значение вводу новых месторождений: это развитие Сузунского месторождения, Лодочное месторождение, Русское, Куюмбинское, Юрубчено-Тохомское [месторождения], Таас-Юрях. И газовые активы: "Роспан", "Харампур", Кынско-Часельское месторождение.

Parsed view: роснефть планировать направить на инвестиционный программа роснефть в 2017 год 1 1 триллион рубль в 2018 год – 1 3 триллион о это рассказать глава компания игорь сечин на встреча с владимир путин в 2017 год компания придать особый значение ввод новый месторождений: это развитие сузунский месторождение лодочный месторождение русский куюмбинский юрубчено-тохомский [месторождения] таас-юрить и газовый активы: роспан харампур кынско-часельское месторождение"""
    print(sentence_info(s))
