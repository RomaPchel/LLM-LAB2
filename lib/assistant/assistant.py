import spacy
from spacy.language import Language
from lib.db.config import conn
from lib.lemmas.lemmas import medication_lemmas
from lib.models.Medication import Medication


class Assistant:
    def __init__(self):
        try:
            self.__nlp = spacy.load("uk_core_news_sm")
            self.__nlp.add_pipe("custom_pipe", last=True)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM medication")
            self.medications_list = cursor.fetchall()
            self.last_intent = ""
            self.last_medication = ""
        except Exception as e:
            print(e)

    def __detect_intent(self, doc):
        for token in doc:
            if token.text.lower() in ["ціна", "ціни", "ціною", "вартість", "вартіст"]:
                return "price_query"
            elif token.text.lower() in ["застосовувати", "приймати", "застосування", "приймання"]:
                return "instruction_query"
            elif token.text.lower() in ["додати", "додай", "запиши", "записати"]:
                return "add_query"
            elif token.text.lower() in ["рекомендація", "рекомендації", "порада", "поради"]:
                return "recommendation_query"
        return "general_query"

    def process_query(self, query):
        doc = self.__nlp(query)
        intent = self.__detect_intent(doc)
        print(intent)
        if intent == "price_query":
            return self.__process_price_query(doc)
        elif intent == "instruction_query":
            return self.__process_instruction_query(doc)
        elif intent == "add_query":
            return self.__save_medication()
        elif intent == "recommendation_query":
            return self.__process_recommendation_query(doc)
        else:
            if self.last_intent == 'price':
                return self.__process_price_query(doc)
            elif self.last_intent == "instruction":
                return self.__process_instruction_query(doc)
            elif self.last_intent == "add":
                return self.__save_medication()
            elif self.last_intent == "recommendation":
                return self.__process_recommendation_query(doc)
            else:
                return "Не розумію"

    def __process_price_query(self, doc):
        medication = self.__get_specific_medication_if_mentioned(doc)
        self.last_intent = "price"
        last_medication = self.last_medication
        if medication:
            print(f"Ціна препарату: {medication.price}")
            return

        if not medication and last_medication:
            print(f"Ціна препарату: {last_medication.price}")
            return

        prices = "Ціни препаратів:\n"
        for medication in self.medications_list:
            prices += Medication(*medication).name + " " + str(Medication(*medication).price) + "\n"
        print(prices)

    def __process_instruction_query(self, doc):
        self.last_intent = "instruction"
        medication = self.__get_specific_medication_if_mentioned(doc)

        if not medication:
            medication = self.last_medication
            print("Інформація не знайдена")

        print(f"Інструкція: {medication.additionalInfo}")

    def __process_recommendation_query(self, doc):
        self.last_intent = "recommendation"
        symptoms = [token.lemma_.lower() for token in doc if token.pos_ in ["NOUN", "ADJ"]]

        if not symptoms:
            print("Вибачте, я не можу надати рекомендації без вказівки на симптоми.")
            return

        print(symptoms)
        recommended_medications = self.__find_medications_by_symptoms(symptoms)

        if not recommended_medications:
            print("На жаль, за вашими симптомами не знайдено рекомендованих препаратів.")
            return
        print(recommended_medications)
        print(f"Рекомендовані препарати для ваших симптомів: {', '.join(recommended_medications)}")



    def __find_medications_by_symptoms(self, symptoms):
        recommended_medications = []
        for medication in self.medications_list:
            med_symptoms = medication[6].split(", ")
            if any(symptom in med_symptoms for symptom in symptoms):
                recommended_medications.append(medication[1])
        return recommended_medications

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
        self.last_intent = 'add'
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




@Language.component("custom_pipe")
def custom_lemmatizer(doc):
    lemma_map = {lemma: key for key, lemmas in medication_lemmas.items() for lemma in lemmas}
    for token in doc:
        if token.text.lower() in lemma_map:
            token.lemma_ = lemma_map[token.text.lower()]
            print(token)

    return doc