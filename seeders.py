from lib.db.config import conn

cursor = conn.cursor()

cursor.execute(
    "INSERT INTO medication (name, usedFor, needsPrescription, price, additionalInfo) VALUES ('Аспірин', 'Зниження температури, знімання болю', FALSE, 12.50, 'Дієтетичний добавок');")
cursor.execute(
    "INSERT INTO medication (name, usedFor, needsPrescription, price, additionalInfo) VALUES ('Ібупрофен', 'Знімання болю, зменшення запалення', FALSE, 18.75, 'Потрібно уникати вживання з іншими препаратами');")
cursor.execute(
    "INSERT INTO medication (name, usedFor, needsPrescription, price, additionalInfo) VALUES ('Антигрипін', 'Лікування грипу та застуди', TRUE, 25.99, 'Вмістить аспірин, парацетамол та антигістамін');")
cursor.execute(
    "INSERT INTO medication (name, usedFor, needsPrescription, price, additionalInfo) VALUES ('Парацетамол', 'Знімання болю, зниження температури', FALSE, 15.20, 'Має протизапальні властивості');");
conn.commit()