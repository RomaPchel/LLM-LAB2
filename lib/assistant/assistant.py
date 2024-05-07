import spacy
from spacy.tokens import Doc
from lib.db.config import conn
from lib.lemmas.lemmas import medication_lemmas
from lib.models.Medication import Medication


class Assistant:
    def __init__(self):
        self.__nlp = spacy.load("uk_core_news_sm")
        self.__nlp.add_pipe(self.__intent_component, last=True)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medication")
        self.medications_list = cursor.fetchall()

    def process_query(self, query):
        doc = self.__nlp(query)
        intent = doc._.intent

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
                print("Не розумію")

    def __process_price_query(self, doc):
        self.last_intent = "price"
        medication = doc._.last_medication
        if medication:
            print(f"Ціна препарату: {medication.price}")
            return

        print("Ціни препаратів:")
        for medication in self.medications_list:
            print(Medication(*medication).name + " " + str(Medication(*medication).price))

    def __process_instruction_query(self, doc):
        self.last_intent = "instruction"
        medication = doc._.last_medication

        if not medication:
            print("Інформація не знайдена")
            return
        print(f"Інструкція: {medication.additionalInfo}")

    def __process_recommendation_query(self, doc):
        self.last_intent = "recommendation"
        symptoms = [token.lemma_.lower() for token in doc if token.pos_ == "NOUN" or token.pos_ == "ADJ"]

        if not symptoms:
            print("Вибачте, я не можу надати рекомендації без вказівки на симптоми.")
            return

        recommended_medications = self.__find_medications_by_symptoms(symptoms)

        if not recommended_medications:
            print("На жаль, за вашими симптомами не знайдено рекомендованих препаратів.")
            return

        print(f"Рекомендовані препарати для ваших симптомів: {', '.join(recommended_medications)}")

    @staticmethod
    def __intent_component(doc):
        intent = "general_query"
        last_medication = None

        for token in doc:
            if token.lower_ in ["ціна", "вартість"]:
                intent = "price_query"
            elif token.lower_ in ["прийом", "приймати", "вживання", "вживати", "інструкція"]:
                intent = "instruction_query"
            elif token.lower_ in ["додай", "додати", "записати", "запиши", "збережи"]:
                intent = "add_query"
            elif token.lower_ in ["рекомендація", "порада", "порадити"]:
                intent = "recommendation_query"
            else:
                medication = Assistant.__find_medication_by_name(token.text.lower())
                if medication:
                    last_medication = Medication(*medication)

        doc._.intent = intent
        doc._.last_medication = last_medication
        return doc

    def __find_medications_by_symptoms(self, symptoms):
        recommended_medications = []
        for medication in self.medications_list:
            med_symptoms = medication[5].split(", ")
            if any(symptom in med_symptoms for symptom in symptoms):
                recommended_medications.append(medication[0])
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

