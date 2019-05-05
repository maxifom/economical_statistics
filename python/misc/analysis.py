import pandas as pd
import pymorphy2

from misc import Database
from misc.database import Database
from models import Company, News, Word

morpher = pymorphy2.MorphAnalyzer()


def sentence_info_pd(x, positive=[], negative=[]):
    words = []
    # splitted = sentence.split('.')
    positives = 0
    negatives = 0
    result = {"sent_score": 0, "word_count": 0}
    sentence = str(x.text).replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(
        ' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    sentence = sentence.split(' ')
    for i in range(len(sentence)):
        c = 0
        while sentence[i] != morpher.parse(sentence[i])[0].normal_form:
            sentence[i] = morpher.parse(sentence[i])[0].normal_form
            c += 1
            if c > 5:
                break
    result["word_count"] = len(sentence)
    result["sentence"] = ' '.join(sentence)
    if not pd.isna(x.title):
        title = str(x.title)
        title = title.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(
            ' ').rstrip(
            ' ').replace('"', '').replace('  ', ' ')
        result["word_count"] += len(title)
        title = title.split(' ')
        for i in range(len(title)):
            c = 0
            while title[i] != morpher.parse(title[i])[0].normal_form:
                title[i] = morpher.parse(title[i])[0].normal_form
                c += 1
                if c > 5:
                    break
        # sentence = '.'.join(splitted[1:])
        result["sentence"] = ' '.join(title) + ' ' + result["sentence"]

        # title
        for p in positive:
            words_to_delete = []
            spl = p.word.split(' ')
            l = len(spl)
            _p = {}
            for i in range(0, len(title)):
                tr = True
                for j in range(0, l):
                    if i + j < len(title):
                        if spl[j] != title[i + j]:
                            tr = False
                            break
                        else:
                            words_to_delete.append(i + j)
                            tr = True
                    else:
                        tr = False
                        break
                if tr:
                    _p["word"] = p.word
                    _p["score"] = 1
                    if "count" not in _p:
                        _p["count"] = 0
                    _p["count"] += 10
                    positives += 10
            new_title = []
            index = 0
            for _ in title:
                if index not in words_to_delete:
                    new_title.append(title[index])
                index += 1
            title = new_title
            words_to_delete = []
            if "word" in _p:
                words.append(_p)
        for p in negative:
            words_to_delete = []
            spl = p.word.split(' ')
            l = len(spl)
            _p = {}
            for i in range(0, len(title)):
                tr = True
                for j in range(0, l):
                    if i + j < len(title):
                        if spl[j] != title[i + j]:
                            tr = False
                            break
                        else:
                            words_to_delete.append(i + j)
                            tr = True
                    else:
                        tr = False
                        break
                if tr:
                    _p["word"] = p.word
                    _p["score"] = -1
                    if "count" not in _p:
                        _p["count"] = 0
                    _p["count"] += 10
                    negatives += 10
            new_title = []
            index = 0
            for s in title:
                if index not in words_to_delete:
                    new_title.append(title[index])
                index += 1
            title = new_title
            words_to_delete = []
            if "word" in _p:
                words.append(_p)
    # print(sentence)
    # print(positive)
    # Text
    for p in positive:
        words_to_delete = []
        spl = p.word.split(' ')
        # print(spl)
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
                _p["word"] = p.word
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
        spl = p.word.split(' ')
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
                _p["word"] = p.word
                _p["score"] = -1
                if "count" not in _p:
                    _p["count"] = 0
                _p["count"] += 1
                negatives += 1
        new_title = []
        index = 0
        for s in sentence:
            if index not in words_to_delete:
                new_title.append(sentence[index])
            index += 1
        sentence = new_title
        words_to_delete = []
        if "word" in _p:
            words.append(_p)
    if positives - negatives != 0:
        result["sent_score"] = (positives - negatives) / (positives + negatives)
    result["words"] = words
    print(x.timestamp)
    return pd.Series([result["sent_score"], result["word_count"], result["words"], result["sentence"]])


def sentence_info(news: News, positive=[], negative=[]):
    if len(positive) == 0 and len(negative) == 0:
        positive = Word.select(Word.word).where(Word.is_positive == 1)
        negative = Word.select(Word.word).where(Word.is_positive == 0)
        positive = sorted(positive, key=lambda x: len(x.word.split(' ')), reverse=True)
        negative = sorted(negative, key=lambda x: len(x.word.split(' ')), reverse=True)
    words = []
    # splitted = sentence.split('.')
    positives = 0
    negatives = 0
    result = {"sent_score": 0, "word_count": 0}
    sentence = str(news.body).replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(
        ' ').rstrip(
        ' ').replace('"', '').replace('  ', ' ')
    sentence = sentence.split(' ')
    for i in range(len(sentence)):
        c = 0
        while sentence[i] != morpher.parse(sentence[i])[0].normal_form:
            sentence[i] = morpher.parse(sentence[i])[0].normal_form
            c += 1
            if c > 5:
                break
    result["word_count"] = len(sentence)
    result["sentence"] = ' '.join(sentence)
    if news.title is not None and news.title.replace(" ", "") != "":
        title = str(news.title)
        title = title.replace('.', ' ').replace(',', ' ').replace('\n', '').replace('\t', '').lstrip(
            ' ').rstrip(
            ' ').replace('"', '').replace('  ', ' ')
        result["word_count"] += len(title)
        title = title.split(' ')
        for i in range(len(title)):
            c = 0
            while title[i] != morpher.parse(title[i])[0].normal_form:
                title[i] = morpher.parse(title[i])[0].normal_form
                c += 1
                if c > 5:
                    break
        # sentence = '.'.join(splitted[1:])
        result["sentence"] = ' '.join(title) + ' ' + result["sentence"]

        # title
        for p in positive:
            words_to_delete = []
            spl = p.word.split(' ')
            l = len(spl)
            _p = {}
            for i in range(0, len(title)):
                tr = True
                for j in range(0, l):
                    if i + j < len(title):
                        if spl[j] != title[i + j]:
                            tr = False
                            break
                        else:
                            words_to_delete.append(i + j)
                            tr = True
                    else:
                        tr = False
                        break
                if tr:
                    _p["word"] = p.word
                    _p["score"] = 1
                    if "count" not in _p:
                        _p["count"] = 0
                    _p["count"] += 10
                    positives += 10
            new_title = []
            index = 0
            for _ in title:
                if index not in words_to_delete:
                    new_title.append(title[index])
                index += 1
            title = new_title
            words_to_delete = []
            if "word" in _p:
                words.append(_p)
        for p in negative:
            words_to_delete = []
            spl = p.word.split(' ')
            l = len(spl)
            _p = {}
            for i in range(0, len(title)):
                tr = True
                for j in range(0, l):
                    if i + j < len(title):
                        if spl[j] != title[i + j]:
                            tr = False
                            break
                        else:
                            words_to_delete.append(i + j)
                            tr = True
                    else:
                        tr = False
                        break
                if tr:
                    _p["word"] = p.word
                    _p["score"] = -1
                    if "count" not in _p:
                        _p["count"] = 0
                    _p["count"] += 10
                    negatives += 10
            new_title = []
            index = 0
            for s in title:
                if index not in words_to_delete:
                    new_title.append(title[index])
                index += 1
            title = new_title
            words_to_delete = []
            if "word" in _p:
                words.append(_p)
    # print(sentence)
    # print(positive)
    # Text
    for p in positive:
        words_to_delete = []
        spl = p.word.split(' ')
        # print(spl)
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
                _p["word"] = p.word
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
        spl = p.word.split(' ')
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
                _p["word"] = p.word
                _p["score"] = -1
                if "count" not in _p:
                    _p["count"] = 0
                _p["count"] += 1
                negatives += 1
        new_title = []
        index = 0
        for s in sentence:
            if index not in words_to_delete:
                new_title.append(sentence[index])
            index += 1
        sentence = new_title
        words_to_delete = []
        if "word" in _p:
            words.append(_p)
    if positives - negatives != 0:
        result["sent_score"] = (positives - negatives) / (positives + negatives)
    result["words"] = words
    return result


def extract_company(news):
    companies = Company.select()
    for c in companies:
        c.parse_name = c.parse_name.split(', ')
    news_with_one_company = []
    for d in news:
        d["companies"] = []
        for c in companies:
            for p in c.parse_name:
                if p in str(d["body"]):
                    d["companies"].append(c.id)
                    break
        if len(d["companies"]) == 1:
            d["company"] = d["companies"][0]
            del d["companies"]
            news_with_one_company.append(d)
    return news_with_one_company


if __name__ == '__main__':
    s = """Чистая прибыль "ФосАгро" в 2018 году снизилась на 13%. Чистая прибыль "ФосАгро" по МСФО в 2018 году снизилась на 13% - до 22,135 млрд рублей, сообщает компания.Выручка составила 233,43 млрд рублей (+29%).Выручка "ФосАгро" за четвертый квартал выросла на 30% до 59,4 млрд рублей (893 млн долларов США), в то время как EBITDA увеличилась на 51% до 18,6 млрд рублей (279 млн долларов США). Таким образом, в четвертом квартале 2018 года рентабельность по EBITDA увеличилась до 31% с 27% годом ранее.Чистая прибыль (скорректированная на неденежные валютные статьи) за четвертый квартал выросла практически в три раза до 10,9 млрд рублей (164 млн долларов США), данный показатель за 2018 год достиг 41,7 млрд рублей (666 млн долларов США)."""
    print(sentence_info(s))
