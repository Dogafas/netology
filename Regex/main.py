import csv
import pandas as pd
import re


# 1. Чтение файла
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

# 2. Преобразуем список в таблицу начиная с 2ой строки, в 1ой строке-заголовки
df = pd.DataFrame(contacts_list[1:], columns=contacts_list[0])

# 3. Очистка и распределение ФИО
def clean_names(row):
    names = []
    for col in ['lastname', 'firstname', 'surname']:
        if pd.notna(row[col]):
            names.extend(row[col].split())
    row['lastname'] = names[0] if len(names) > 0 else None
    row['firstname'] = names[1] if len(names) > 1 else None
    row['surname'] = names[2] if len(names) > 2 else None
    return row

df = df.apply(clean_names, axis=1) # применим сlean_names к каждой строке

# 4. Приведение телефонов к нужному формату
def format_phone(phone):
    phone = re.sub(r'(\+?7|8)?\s*\(?(\d{3})\)?\s*-?(\d{3})\s*-?(\d{2})\s*-?(\d{2})', r'+7(\2)\3-\4-\5', phone)
    phone = re.sub(r'\s*\(доб\.\s*(\d+)\)', r' доб.\1', phone)
    phone = re.sub(r'\s*доб\.\s*(\d+)', r' доб.\1', phone)
    return phone

df['phone'] = df['phone'].apply(format_phone) # Применим функцию format_phone ко всем значениям из столбца phone

# 5. Объединение дублирующихся записей 
def merge_fields(group):
    merged = group.fillna('').groupby(['lastname', 'firstname']).agg(lambda x: ''.join(x.dropna().unique())).reset_index()
    return merged

df_cleaned = merge_fields(df)

# Сохранение данных в новый файл
df_cleaned.to_csv('phonebook.csv', index=False)


