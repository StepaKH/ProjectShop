import openpyxl


def check_card_status(filename, full_name):
    # Загружаем файл Excel
    wb = openpyxl.load_workbook(filename, read_only=True)
    ws = wb.active

    # Проходим по значениям в первом столбце и ищем совпадение с заданным именем
    for row in ws.iter_rows(min_row=1, max_col=1, values_only=True):
        if row[0] == full_name:
            return 1  # Карта найдена
    return 0  # Карта не найдена


def create_card(filename, fio):
    # Загружаем файл Excel
    wb = openpyxl.load_workbook(filename)
    ws = wb.active

    # Находим номер последней заполненной строки
    last_row = ws.max_row

    # Вписываем ФИО в последнюю свободную строку
    ws.cell(row=last_row + 1, column=1).value = fio

    # Сохраняем изменения в файле
    wb.save(filename)
