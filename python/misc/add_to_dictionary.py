import pymorphy2
from models import Word

morpher = pymorphy2.MorphAnalyzer()


def add_words_from_txt(file, is_positive=1):
    with open(file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    process_lines(lines, is_positive)


def process_lines(lines, is_positive):
    for line in lines:
        process_line(line, is_positive)


def process_line(line, is_positive):
    line = line.replace("\r", "").replace("\n", "").lower()
    spl = line.split(' ')
    if len(spl) > 1:
        for _i in range(0, len(spl)):
            c = 0
            while spl[_i] != morpher.parse(spl[_i])[0].normal_form:
                spl[_i] = morpher.parse(spl[_i])[0].normal_form
                c += 1
                if c > 5:
                    break
        line = ' '.join(spl)
    else:
        c = 0
        while line != morpher.parse(line)[0].normal_form:
            line = morpher.parse(line)[0].normal_form
            c += 1
            if c > 5:
                break
    Word.insert(word=line, is_positive=is_positive).on_conflict_ignore().execute()

