import spacy
from lib.db.config import conn
from lib.lemmas.lemmas import medication_lemmas
from lib.models.Medication import Medication


class Assistant:
    def __init__(self):
        self.__nlp = spacy.load("uk_core_news_sm")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medication")
        self.medications_list = cursor.fetchall()

    def process_query(self, query):
        doc = self.__nlp(query)
        intent = self.__detect_intent(doc)
        if intent == "price_query":
            return self.__process_price_query(doc)
        elif intent == "size_query":
            return self.__process_size_query(doc)
        elif intent == "recommendation_query":
            return self.__process_recommendation_query(doc)
        else:
            return "Вибачте, я не розумію ваш запит."

    def __process_price_query(self, doc):
        medication = self.__get_specific_medication_if_mentioned(doc)
        if medication:
            print(f"Ціна препарату: {medication.price}")
            return

        print("Ціни препаратів:")
        for medication in self.medications_list:
            print(Medication(*medication).name + " " + str(Medication(*medication).price))

    def __process_recommendation_query(self, doc):
        print(doc)
        return "Список рекомендацій: ..."

    def __detect_intent(self, doc):
        for token in doc:
            if token.text.lower() in ["ціна", "ціни", "ціною", "вартість", "вартіст"]:
                return "price_query"
            elif token.text.lower() in ["розмір", "розміри", "розміром"]:
                return "size_query"
            elif token.text.lower() in ["рекомендація", "рекомендації", "порада", "поради"]:
                return "recommendation_query"
        return "general_query"

    def __get_specific_medication_if_mentioned(self, doc):
        for token in doc:
            medication = self.__find_medication_by_name(token.text.lower())
            if medication:
                return Medication(*medication)
        return None

    def __find_medication_by_name(self, name):
        name_lemma = self.__get_lemma(name.lower())
        for med_name, med_lemmas in medication_lemmas.items():
            if name_lemma in med_lemmas:
                for medication in self.medications_list:
                    if medication[1].lower() == str(med_name):
                        return medication
        return None

    def __get_lemma(self, word):
        return self.__nlp(word)[0].lemma_

    def __save_medication(self):
        name = input("Напишіть назву препарату: ")
        price = float(input("Напишіть ціну препарату: "))
        usedFor = input("Напишіть для чого застосовується препарат: ")
        needsPrescription_input = input("Напишіть чи потрібен рецепт (y/n): ")
        needsPrescription = True if needsPrescription_input.lower() == 'y' else False
        additionalInfo = input("Напишіть додаткову інформацію: ")
        symptoms = input("Напишіть симптоми, що лікуються препаратом: ")

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medication (name, price, usedFor, needsPrescription, additionalInfo, symptoms) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, price, usedFor, needsPrescription, additionalInfo, symptoms))
        conn.commit()

        self.medications_list.append((name, price, usedFor, additionalInfo, symptoms))
        print("Препарат успішно додано до бази даних.")