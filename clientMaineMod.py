import sys
import requests

base_url = "https://api.trello.com/1/{}"
board_id = "iHepLVxm"

# Данные авторизации. Можете заменить на свои данные в API Trello. Я свою доску сотру через неделю.
auth_params = {
    'key': "b964e94634a93a36833ceeaab5a67d6b",
    'token': "8b523d8866df6f78c4cb96c57660be68b71c3e79cbac4de25ce51049dc17bafb", }

def read_tasks ():
    task_counter = 0
    # Получим названия всех колонок на доске и названия зададач в колонке
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        # Получим названия всех задач в  каждой колонке и выведем на экран все названия задач и их ID
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(f"\n{column['name']} ({len(task_data)})")
        if not task_data:
            print('\t' + '--Нет задач--')
            continue
        for task in task_data:
            task_counter += 1
            #print(task_counter)
            print(f"\t {task_counter} {task['name']} \t \n             id: {task['id']}")
    print("\n")

def create_tasks (name, column_name):
    # Получим названия всех колонок на доске и названия зададач в колонке
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    column_names = []
    for column in column_data:
        column_names.append(column['name'])
        if column['name'] == column_name:
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            print("\nЗадача создана")
            read_tasks()
            exit()
    if column_name not in column_names:
        print(f"\nСписок << {column_name} >> не найден. Все задачи:")
        read_tasks()

def move_tasks (name, column_name):
    # Получим названия всех колонок на доске и названия зададач в колонке
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Находим все задачи с указанным именем
    search, column_names = [], []
    for column in column_data:
        column_names.append(column['name'])
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                search.append((task['id'], column['name']))
    if column_name not in column_names or not search:
        print(f"\nСписок << {column_name} >> или задача << {name} >> не найдены. Все задачи:")
        read_tasks()
        exit()

    choice = 0

    # в случае нескольких задач с одинаковым содержимым
    if len(search) > 1:
        print(f'У вас несколько задач с названием "{name}":')
        for id in search:
            print(f"{search.index(id) + 1} id: {id[0]} в списке {id[1]}")
        while True:
            try:
                choice = int(input(f"Выберите ID нужной задачи (1-{len(search)}): ")) - 1
                if choice not in range(len(search)):
                    print("Введено некорректное значение")
                    continue
                elif search[choice][1] == column_name:
                    print("Задача уже находится в указанном списке")
                    exit()
                id = search[choice][0]
                break
            except (IndexError, ValueError):
                print("Введено некорректное значение")
                continue

    id = search[choice][0]
    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + id + '/idList', data={'value': column['id'], **auth_params})
            print("Задача перемещена")
     
def new_column(column_name):
    board_info = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
    requests.post(base_url.format('lists') + '/', data={'name': column_name, 'idBoard': board_info['id'], **auth_params})
    print(f"Список {column_name} создан")
    read_tasks()


def usage():
    print("\nUsage:\n\tpython client.py \t - Список всех задач\
                \n\tpython client.py <options>\
                \n\t\t new <column_name> \t\t - Создать колонку <column_name>\
                \n\t\t create <name> <column_name> \t - Cоздать задачу <name> в колонке <column_name>\
                \n\t\t move <name> <column_name> \t - Переместить задачу <name> в колонку <column_name>\n")

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            read_tasks()
        elif sys.argv[1] == 'create':
            create(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'move':
            move(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'new':
            new_column(sys.argv[2])
        else:
            usage()
    except IndexError:
        usage()

