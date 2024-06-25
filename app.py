from flask import Flask, request, jsonify
import random
import os
from datetime import date

app = Flask(__name__)


# Функции для работы с файлами
def write_to_file(text="Правильных ответов: 0 | Неправильных ответов: 0"):
    today = date.today()
    with open(f"{today}.txt", "w+") as my_file:
        my_file.write(text)


def get_data_from_file():
    today = date.today()
    if not os.path.isfile(f"{today}.txt"):
        write_to_file()
    with open(f"{today}.txt", "r") as my_file:
        res_list = my_file.readline().split(" | ")
    return res_list


def write_data_to_file(true_or_false):
    user_res = get_data_from_file()
    if true_or_false:
        total = int(user_res[0].split(": ")[1]) + 1
        res = f"Правильных ответов: {total} | {user_res[1]}"
    else:
        total = int(user_res[1].split(": ")[1]) + 1
        res = f"{user_res[0]} | Неправильных ответов: {total}"
    write_to_file(res)


# Генерация задачи
def generate_example():
    x = random.randint(3, 9)
    y = random.randint(3, 9)
    type_example = random.randint(1, 2)
    if type_example == 1:
        example = f"{x} * {y} = ?"
        right_answer = x * y
    else:
        res = x * y
        example = f"{res} / {y} = ?"
        right_answer = res / y
    return example, right_answer


user_answers = {}


@app.route('/alice', methods=['POST'])
def alice_skill():
    req = request.json
    user_id = req['session']['user_id']
    command = req['request']['command'].lower()

    if command == 'старт' or command == 'start':
        response_text = "Привет! Скажи 'задача', чтобы получить задачу на умножение или деление."
    elif command == 'задача' or command == 'task':
        example, right_answer = generate_example()
        user_answers[user_id] = right_answer
        response_text = example
    elif command == 'результат' or command == 'result':
        res_list = get_data_from_file()
        response_text = f"ℹ️ Сегодня:\n{res_list[0]}\n{res_list[1]}\n\nСкажи 'задача', чтобы продолжить."
    elif command.isdigit():
        user_answer = int(command)
        right_answer = user_answers.get(user_id)

        if right_answer is None:
            response_text = "Скажи 'задача', чтобы получить задачу."
        elif user_answer == right_answer:
            response_text = f"🏆 Молодец! Это правильный ответ!\n\nПосмотреть статистику за сегодня, скажи 'результат'."
            write_data_to_file(True)
        else:
            response_text = f"❌ Неправильно. Правильный ответ: {int(right_answer)}\n\nПосмотреть статистику за сегодня, скажи 'результат'."
            write_data_to_file(False)

        # Удаляем правильный ответ после проверки
        user_answers.pop(user_id, None)
        example, right_answer = generate_example()
        user_answers[user_id] = right_answer
        response_text += f"\n\nВот новая задача: {example}"
    else:
        response_text = "Я не понимаю этот запрос. Скажи 'задача', чтобы получить задачу."

    res = {
        "version": req['version'],
        "session": req['session'],
        "response": {
            "text": response_text,
            "end_session": False
        }
    }
    return jsonify(res)


if __name__ == '__main__':
    app.run(port=5000)
