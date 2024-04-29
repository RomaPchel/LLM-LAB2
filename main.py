from lib.assistant.assistant import Assistant


def main():
    print("Вітаємо! Я віртуальний медичний асистент.")
    print("Запитуйте про ціни, інструкції або отримуйте рекомендації на основі сиптомів.")
    assistant = Assistant()
    while True:
        query = input("Ваш запит: ")
        if query.lower() in ["вийти", "завершити", "кінець", "до побачення"]:
            print("До побачення!")
            break
        else:
            assistant.process_query(query)


if __name__ == "__main__":
    main()
