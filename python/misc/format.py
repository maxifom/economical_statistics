class Formatter:
    @staticmethod
    def format_volume(volume):
        if 'K' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('K', '')) * 1e3
        elif 'M' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('M', '')) * 1e6
        elif 'B' in volume:
            volume = float(volume.replace('.', '').replace(',', '.').replace('B', '')) * 1e9
        return int(volume)

    @staticmethod
    def format_price(price):
        return float(price.replace('.', '').replace(',', '.'))
