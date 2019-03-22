import pymorphy2
from database import Database

morpher = pymorphy2.MorphAnalyzer()


def positive_from_txt(file):
    with open(file, 'r') as file:
        lines = file.readlines()
    for i in range(0, len(lines)):
        spl = lines[i].split(' ')
        if len(spl) > 1:
            for _i in range(0, len(spl)):
                spl[_i] = spl[_i].rstrip('\n').lower()
                c = 0
                while spl[_i] != morpher.parse(spl[_i])[0].normal_form:
                    spl[_i] = morpher.parse(spl[_i])[0].normal_form
                    c += 1
                    if c > 5:
                        break
            lines[i] = ' '.join(spl)
        else:
            lines[i] = lines[i].rstrip('\n').lower()
            c = 0
            while lines[i] != morpher.parse(lines[i])[0].normal_form:
                lines[i] = morpher.parse(lines[i])[0].normal_form
                c += 1
                if c > 5:
                    break
    db = Database()
    for l in lines:
        db.db.execute("""
               INSERT IGNORE INTO words(word,is_positive) VALUES(%s,%s)
           """, (l, 1))
    db.connection.commit()


def negative_from_txt(file):
    with open(file, 'r') as file:
        lines = file.readlines()
    for i in range(0, len(lines)):
        spl = lines[i].split(' ')
        if len(spl) > 1:
            for _i in range(0, len(spl)):
                spl[_i] = spl[_i].rstrip('\n').lower()
                c = 0
                while spl[_i] != morpher.parse(spl[_i])[0].normal_form:
                    spl[_i] = morpher.parse(spl[_i])[0].normal_form
                    c += 1
                    if c > 5:
                        break
            lines[i] = ' '.join(spl)
        else:
            lines[i] = lines[i].rstrip('\n').lower()
            c = 0
            while lines[i] != morpher.parse(lines[i])[0].normal_form:
                lines[i] = morpher.parse(lines[i])[0].normal_form
                c += 1
                if c > 5:
                    break
    db = Database()
    for l in lines:
        db.db.execute("""
            INSERT IGNORE INTO words(word,is_positive) VALUES(%s,%s)
        """, (l, 0))
    db.connection.commit()


if __name__ == '__main__':
    positive_from_txt("positive.txt")
    negative_from_txt("negative.txt")
