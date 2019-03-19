class DateToHexConverter:
    @staticmethod
    def to_hex(date):
        return DateToHexConverter.hex_of(date.day) + \
               DateToHexConverter.hex_of(date.month) + \
               DateToHexConverter.hex_of(date.year)

    @staticmethod
    def hex_of(num):
        h = hex(num).replace('0x', '').upper()
        if len(h) == 1:
            h = '0' + h
        return h
