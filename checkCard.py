import openpyxl

def check_card_status(filename, full_name):
    # Загружаем файл Excel
    wb = openpyxl.load_workbook(filename, read_only=True)
    ws = wb.active

    # Проходим по значениям в первом столбце и ищем совпадение с заданным именем
    for row in ws.iter_rows(min_row=1, max_col=1, values_only=True):
        if row[0] == full_name:
            print(row[0])
            return True  # Карта найдена
    return False  # Карта не найдена