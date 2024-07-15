import os
import re
from bs4 import BeautifulSoup
import random

ASCII_TREE = {
    'root_opening': '┏━━ ',
    'branch_branch': '├── ',
    'branch_closing': '└── ',
    'branch_vertical': '│   ',
    'space': '    ',
    'root_closing': '┗━━ ',
    'root_vertical': '┃   '
}

INDENT_TREE = {
    'root_opening': '',
    'branch_branch': '',
    'branch_closing': '',
    'branch_vertical': '',
    'space': '  ',
    'root_closing': '',
    'root_vertical': '  '
}

LANG = {
    'en': {
        'tree': 'TREE',
        'branch': 'BRANCH',
        'input_level': "\nYou can specify the starting level for random path generation. The path generation initiates at the chosen level and descends recursively until encountering a childless <h1> or <p> tag. At this point, it returns to the originating level and begins anew, or, if no further elements exist at that level, proceeds to the next branch, tree, or file.\n\nTo illustrate this process:\n\nStarting Level 1:\n\n[№01-h01-ID] Character: line...\n└── [№02-h01-ID] Hero: reply...\n   └── [№03-h01-ID] Character: line...\n       └── [№04-h01-ID] Hero: reply...\n           └── [№05-h01-ID] Character: line...\n               ├── [№06-p01-ID] Hero: reply...\n               │   └── [№07-h01-ID] Character: line...\n               └── [№08-p02-ID] (X) Hero: reply, ends the dialogue...\n\nStarting Level 2:\n\n[№01-h01-ID] Character: line...\n├── [№02-h01-ID] Hero: reply...\n│   └── [№03-h01-ID] Character: line...\n│       └── [№04-p02-ID] Hero: reply...\n│           └── [№05-h01-ID] Character: line...\n│               ├── [№06-p01-ID] (X) Hero: reply, ends the dialogue...\n└── [№02-h02-ID] Hero: reply...\n   └── [№03-h01-ID] Character: line...\n       └── [№04-h01-ID] Hero: reply...\n           └── [№05-h01-ID] Character: line...\n               ├── [№06-p01-ID] Hero: reply...\n               │   └── [№07-h01-ID] Character: line...\n               └── [№08-p02-ID] (X) Hero: reply, ends the dialogue...\n\nThe randomizer prioritizes tags with children, favoring continuation over dialogue termination when encountering two such tags.\n\n(↓) appears only at or before the chosen level. <p> tags beyond the chosen level are not marked.\n\nEnter your desired starting level: ",
        'invalid_input': "Please enter a valid non-negative integer.",
        'processing_started': "\nStarting HTML file processing",
        'processing_completed': "HTML file processing completed successfully",
        'total_processed': "Total files processed: {}",
        'error_processing': "An error occurred while processing files: {}",
        'script_completed': "Script execution completed",
        'press_enter': "Press Enter to restart, R to change settings, or Q to quit: ",
        'processing_file': "Processing file: {}",
        'finished_file': "Processed {} → {}",
        'list_processed': "List of all processed files:",
        'no_files_processed': "No files were processed.",
        'choose_language': "Choose language (en/ru): ",
        'invalid_choice': "Invalid choice. Please enter 'en' for English or 'ru' for Russian.",
        'choose_txt_type': """\n\n--- START OF THE ENTRY ---\n\n\nThis script is designed to extract data from HTML files while preserving its hierarchical structure. The script primarily searches for the class attribute within <h1> heading tags (e.g., <h1 class="###">#.</h1>). However, if the <h1> tag lacks a class attribute (e.g., <h1>#.Character, # replies</h1>), the script then searches for class attributes within nearby <p> paragraph tags (e.g., <p class="###">#.</p><p class="###">#). The extracted class number is then matched with identifiers provided in the inarr= parameter, and the corresponding text from the textarr= parameter is retrieved based on the found identifiers. The output file follows this format:\n\n********************\nTREE 1 - BRANCH 1\nHero and Character\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n┃   │   └── [№03-h01-ID] Character: line...\n┃   │       ├── [№04-p01-ID] (↓) Hero: reply, leads to the same line...\n┃   │       └── [№04-p02-ID] (↓) Hero: reply, leads to the same line...\n┃   │           └── [№05-h01-ID] Character: line...\n┃   │               ├── [№06-p01-ID] (X) Hero: reply, ends the dialogue...\n┃   │               └── [№06-p02-ID] (X) Hero: reply, ends the dialogue...\n┃   └── [№02-h02-ID] Hero: reply...\n┃       └── [№03-h01-ID] Character: line...\n┃           └── [№04-h01-ID] Hero: reply...\n┃               └── [№05-h01-ID] Character: line...\n┃                   ├── [№06-p01-ID] (↓) Hero: reply, leads to the same line...\n┃                   └── [№06-p02-ID] (↓) Hero: reply, leads to the same line...\n┃                       └── [№07-h01-ID] Character: line...\n┃                           ├── [№08-p01-ID] (X) Hero: reply, ends the dialogue...\n┗━━                         └── [№08-p02-ID] (X) Hero: reply, ends the dialogue...\n\n********************\nTREE 1 - BRANCH 2\nHero and Character\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n\n********************\nTREE 2 - BRANCH 1\nHero and Character, Day #\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n\n"TREE #":  Indicates the start of a new header (e.g., <div data-role="header"> <h1>Haruspex & Peter Stamatin</h1>). The number increments with each header found.\n"BRANCH #": Indicates the start of a new dialogue. The number increments with each new dialogue within the current tree.\n"Hero and Character": Text extracted from the header (e.g., <div data-role="header"> <h1>Haruspex & Peter Stamatin</h1>).\n"№##": Displays the level of depth in the hierarchy.\n"h/p##": Displays the sequence number of the <h1> or <p> tag at the current level.\n"ID": The number extracted from the class= attribute. Corresponds to strings IDs in main.dat of Pathologic Alpha / 2005 / Classic. In Pathologic 2, the situation is more complex.\n"(↓)": Indicates that all replies lead to the same line located one level below. Used only for <p> tags, which are only extracted if the structure <h1>#.Character, # replies</h1><p class="###">#.</p><p class="###"># is present.\n"(X)": Indicates that the current level has no children (in the game, such a reply should end the dialogue).\n\n\n--- END OF THE ENTRY ---\nADDENDUM: Unlike the full version, this script is intended to generate a random path.\n\n\nTwo options are available for visualizing the tree structure: FULL and SIMPLE.\n\n- FULL mode: Displays the level number, <h1>/<p> number, and ID. It also marks <p> tags(↓) and the end of the dialogue (X).\n\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n\n- SIMPLE mode: Omits all the aforementioned elements.\n\n┏━━ Character: line...\n┃   ├── Hero: reply...\n\nYour choice: (full/simple, lowercase): """,
        'invalid_txt_choice': "Invalid choice. Please enter 'full' or 'simple'.",
        'choose_tree_style': "\nTwo options are available for visualizing the tree structure: using ASCII characters or indentation.\n\n- ASCII Representation: This option employs ASCII characters to depict the tree structure.\n\n┏━━ [№01-h01-ID] Character: Dialogue...\n┃   ├── [№02-h01-ID] Hero: Response...\n┃   │   └── [№03-h01-ID] Character: Dialogue...\n┃   │       ├── [№04-p01-ID] (X) Hero: Dialogue-ending response...\n┃   │       └── [№04-p02-ID] (X) Hero: Dialogue-ending response...\n┗━━ └── [№02-h02-ID] (X) Hero: Dialogue-ending response...\n\n- Indentation Representation: This option utilizes spaces to create indentations that represent the tree structure.\n\n[№01-h01-ID] Character: Dialogue...\n [№02-h01-ID] Hero: Response...\n   [№03-h01-ID] Character: Dialogue...\n     [№04-p01-ID] (X) Hero: Dialogue-ending response...\n     [№04-p02-ID] (X) Hero: Dialogue-ending response...\n [№02-h02-ID] (X) Hero: Dialogue-ending response...\n\nYour choice (ascii/indent, lowercase): ",
        'invalid_tree_choice': "Invalid choice. Please enter 'ascii' or 'indent'.",
        'changing_settings': "Changing settings...",
        'quitting': "Quitting the script...",
        'invalid_restart_choice': "Invalid choice. Press Enter to restart, R to change settings, or Q to quit.",
        'restarting': "Restarting the script...",
    },
    'ru': {
        'tree': 'ДРЕВО',
        'branch': 'ВЕТВЬ',
        'input_level': "\nВы можете задать начальный уровень для генерации случайного пути. Генерация пути начинается с выбранного уровня и рекурсивно спускается вниз до тех пор, пока не встретит тег <h1> или <p> без дочерних элементов. В этот момент генерация возвращается на исходный уровень и начинается заново, либо, если на этом уровне больше нет элементов, переходит к следующей ветви, дереву или файлу.\n\nДля иллюстрации процесса:\n\nНачальный уровень 1:\n\n[№01-h01-ID] Персонаж: реплика...\n└── [№02-h01-ID] Герой: ответ...\n   └── [№03-h01-ID] Персонаж: реплика...\n       └── [№04-h01-ID] Герой: ответ...\n           └── [№05-h01-ID] Персонаж: реплика...\n               ├── [№06-p01-ID] Герой: ответ...\n               │   └── [№07-h01-ID] Персонаж: реплика...\n               └── [№08-p02-ID] (X) Герой: ответ, завершающий диалог...\n\nНачальный уровень 2:\n\n[№01-h01-ID] Персонаж: реплика...\n├── [№02-h01-ID] Герой: ответ...\n│   └── [№03-h01-ID] Персонаж: реплика...\n│       └── [№04-p02-ID] Герой: ответ...\n│           └── [№05-h01-ID] Персонаж: реплика...\n│               ├── [№06-p01-ID] (X) Герой: ответ, завершающий диалог...\n└── [№02-h02-ID] Герой: ответ...\n   └── [№03-h01-ID] Персонаж: реплика...\n       └── [№04-h01-ID] Герой: ответ...\n           └── [№05-h01-ID] Персонаж: реплика...\n               ├── [№06-p01-ID] Герой: ответ...\n               │   └── [№07-h01-ID] Персонаж: реплика...\n               └── [№08-p02-ID] (X) Герой: ответ, завершающий диалог...\n\nГенератор отдает приоритет тегам с дочерними элементами, предпочитая продолжение диалога его завершению при наличии двух таких тегов.\n\n(↓) появляется только на выбранном уровне или до него. Теги <p> за пределами выбранного уровня не отмечены.\n\nВведите желаемый начальный уровень: ",
        'invalid_input': "Пожалуйста, введите корректное неотрицательное целое число.",
        'processing_started': "\nНачинается обработка HTML файлов",
        'processing_completed': "Обработка HTML файлов успешно завершена",
        'total_processed': "Всего обработано файлов: {}",
        'error_processing': "Произошла ошибка при обработке файлов: {}",
        'script_completed': "Выполнение скрипта завершено",
        'press_enter': "Нажмите Enter для перезапуска, R для изменения настроек или Q для выхода: ",
        'processing_file': "Обработка файла: {}",
        'finished_file': "Обработан {} → {}",
        'list_processed': "Список всех обработанных файлов:",
        'no_files_processed': "Файлы не были обработаны.",
        'choose_language': "Выберите язык (en/ru, нижний регистр): ",
        'invalid_choice': "Неверный выбор. Пожалуйста, введите 'en' для английского или 'ru' для русского (нижний регистр).",
        'choose_txt_type': """\n\n-- НАЧАЛО ВСТУПЛЕНИЯ ---\n\n\nДанный скрипт предназначен для извлечения данных из HTML-файлов с сохранением их иерархической структуры. Скрипт в первую очередь ищет атрибут class внутри тегов заголовков <h1> (<h1 class="###">#.</h1>), но если у тега <h1> отсутствует атрибут class (например, <h1>#.Персонаж, # реплики</h1>),  осуществляет поиск атрибутов class у ближайших тегов параграфов <p> (<p class="###">#.</p><p class="###">#). Номер класса сопоставляется с идентификаторами, предоставленными в параметре inarr=, а из параметра textarr= извлекается текст, соответствующий найденным идентификаторам. Выходной файл имеет следующий формат:\n\n********************\nДРЕВО 1 - ВЕТВЬ 1\nГерой и Персонаж\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n┃   │   └── [№03-h01-ID] Персонаж: реплика...\n┃   │       ├── [№04-p01-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃   │       └── [№04-p02-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃   │           └── [№05-h01-ID] Персонаж: реплика...\n┃   │               ├── [№06-p01-ID] (X) Герой: ответ, завершает диалог...\n┃   │               └── [№06-p02-ID] (X) Герой: ответ, завершает диалог...\n┃   └── [№02-h02-ID] Герой: ответ...\n┃       └── [№03-h01-ID] Персонаж: реплика...\n┃           └── [№04-h01-ID] Герой: ответ...\n┃               └── [№05-h01-ID] Персонаж: реплика...\n┃                   ├── [№06-p01-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃                   └── [№06-p02-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃                       └── [№07-h01-ID] Персонаж: реплика...\n┃                           ├── [№08-p01-ID] (X) Герой: ответ, завершает диалог...\n┗━━                         └── [№08-p02-ID] (X) Герой: ответ, завершает диалог...\n\n********************\nДРЕВО 1 - ВЕТВЬ 2\nГерой и Персонаж\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n\n********************\nДРЕВО 2 - ВЕТВЬ 1\nГерой и Персонаж, День #\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n\n"ДРЕВО #": Обозначает начало нового заголовка (например, <div data-role="header"> <h1>Гаруспик & Петр Стаматин</h1>). Номер увеличивается с каждым найденным заголовком.\n"ВЕТВЬ #": Обозначает начало нового диалога. Номер увеличивается с каждым новым диалогом в рамках текущего дерева.\n"Герой и Персонаж": Текст, извлеченный из заголовка (например, <div data-role="header"> <h1>Гаруспик & Петр Стаматин</h1>).\n"№##":  Отображает уровень погружения в иерархию.\n"h/p##":  Отображает порядковый номер тега <h1> или <p> на текущем уровне.\n"ID":  Номер, извлеченный из атрибута class=. Соответствует strings ID в main.dat Pathologic Alpha / 2005 / Classic. В Pathologic 2 ситуация сложнее.\n"(↓)": Указывает, что все ответы ведут к одной и той же реплике, расположенной на уровень ниже. Используется только для тегов <p>, которые извлекаются только при наличии структуры <h1>#.Персонаж, # реплик</h1><p class="###">#.</p><p class="###">#.\n"(X)":  Указывает, что текущий уровень не имеет дочерних элементов (в игре такой ответ должен завершать диалог).\nПРИМЕЧАНИЕ: В отличие от полной версии, данный скрипт предназначен для генерации случайного пути.\n\n\n-- КОНЕЦ ВСТУПЛЕНИЯ ---\n\n\nПредлагается два варианта отображения древовидной структуры: ПОЛНЫЙ и УПРОЩЕННЫЙ.\n\n- Полный вариант: Отображает номер уровня, номер <h1>/<p>, а также идентификатор. Отмечает теги <p> (↓) и конец диалога (X).\n\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n\n- Упрощенный вариант: Не отображает ничего из вышеперечисленного.\n\n┏━━ Персонаж: реплика...\n┃   ├── Герой: ответ...\n\nВаш выбор: (full/simple, нижний регистр): """,
        'invalid_txt_choice': "Неверный выбор. Пожалуйста, введите 'full' или 'simple' (нижний регистр).",
        'choose_tree_style': "\nПредлагается два варианта отображения древовидной структуры: с использованием ASCII-символов и с использованием отступов.\n- ASCII: В данном варианте структура дерева отображается с помощью символов ASCII.\n\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n┃   │   └── [№03-h01-ID] Персонаж: реплика...\n┃   │       ├── [№04-p01-ID] (X) Герой: ответ, завершающий диалог...\n┃   │       └── [№04-p02-ID] (X) Герой: ответ, завершающий диалог...\n┗━━ └── [№02-h02-ID] (X) Герой: ответ, завершающий диалог...\n\n- Отступы: В данном варианте структура дерева отображается с помощью пробелов, формирующих отступы.\n\n[№01-h01-ID] Персонаж: реплика...\n [№02-h01-ID] Герой: ответ...\n   [№03-h01-ID] Персонаж: реплика...\n     [№04-p01-ID] (X) Герой: ответ, завершающий диалог...\n     [№04-p02-ID] (X) Герой: ответ, завершающий диалог...\n [№02-h02-ID] (X) Герой: ответ, завершающий диалог...\n\nВаш выбор (ascii/indent, нижний регистр): ",
        'invalid_tree_choice': "Неверный выбор. Пожалуйста, введите 'ascii' или 'indent' (нижний регистр).",
        'changing_settings': "Изменение настроек...",
        'quitting': "Выход из скрипта...",
        'invalid_restart_choice': "Неверный выбор. Нажмите Enter для перезапуска, R для изменения настроек или Q для выхода.",
        'restarting': "Перезапуск скрипта...",
    }
}

current_lang = 'ru'
txt_type = 'full'
tree_style = ASCII_TREE

def get_p_tag_level_and_count(p_counter, current_h1_level):
    if current_h1_level not in p_counter:
        p_counter[current_h1_level] = {'level': current_h1_level * 1, 'count': 0}
    p_counter[current_h1_level]['count'] += 1
    return (p_counter[current_h1_level]['level'], p_counter[current_h1_level]['count'])

def select_random_path(children):
    h1_with_children = [child for child in children if child.find('div', {'data-role': 'collapsible'})]
    if h1_with_children:
        selected = random.choice(h1_with_children)
    else:
        selected = random.choice(children)
    return selected

def select_random_p(p_tags):
    if p_tags:
        selected = random.choice(p_tags)
        return [selected]
    return []

def choose_tree_style():
    global tree_style
    while True:
        choice = input(LANG[current_lang]['choose_tree_style']).lower()
        if choice == 'ascii':
            tree_style = ASCII_TREE
            break
        elif choice == 'indent':
            tree_style = INDENT_TREE
            break
        else:
            print(LANG[current_lang]['invalid_tree_choice'])

def extract_dialogue_structure(element, level=0, random_selection_level=2, tree_counter=0, branch_counter=0, prefix=''):
    dialogue = []
    level_counter = {}
    p_counter = {}
    last_h1 = None
    p_tags_indices = []
    children = element.find_all('div', {'data-role': 'collapsible'}, recursive=False)
    if level >= random_selection_level and children:
        selected_child = select_random_path(children)
        children = [selected_child]
    for i, child in enumerate(children):
        h1_tags = child.find_all('h1', recursive=False)
        if h1_tags:
            for h1_tag in h1_tags:
                level_match = re.match(r'(\d+)', h1_tag.text.strip())
                if level_match:
                    current_level = int(level_match.group(1))
                else:
                    current_level = level + 1
                if current_level == 1:
                    level_counter = {}
                    p_counter = {}
                    branch_counter += 1
                if current_level not in level_counter:
                    level_counter[current_level] = 0
                level_counter[current_level] += 1
                if h1_tag.get('class'):
                    class_number = h1_tag.get('class')[0]
                    if txt_type == 'full':
                        level_str = f"[№{current_level:02d}-h{level_counter[current_level]:02d}-{class_number}]"
                    else:
                        level_str = ""
                    tree_prefix = tree_style['root_opening'] if current_level == 1 else prefix + (tree_style['branch_closing'] if i == len(children) - 1 else tree_style['branch_branch'])
                    dialogue.append((current_level, level_str, h1_tag.text.strip(), h1_tag.get('class'), tree_prefix, tree_counter, branch_counter))
                    last_h1 = len(dialogue) - 1
                else:
                    p_tags = child.find_all('p', class_=True, recursive=False)
                    if level >= random_selection_level:
                        p_tags = select_random_p(p_tags)
                    p_tags_indices = []
                    for j, p_tag in enumerate(p_tags):
                        p_level, p_count = get_p_tag_level_and_count(p_counter, current_level)
                        class_number = p_tag.get('class')[0]
                        if txt_type == 'full':
                            level_str = f"[№{p_level:02d}-p{p_count:02d}-{class_number}]"
                        else:
                            level_str = ""
                        tree_prefix = prefix + (tree_style['branch_closing'] if i == len(children) - 1 and j == len(p_tags) - 1 else tree_style['branch_branch'])
                        dialogue.append((p_level, level_str, p_tag.text.strip(), p_tag.get('class'), tree_prefix, tree_counter, branch_counter))
                        p_tags_indices.append(len(dialogue) - 1)
        new_prefix = prefix + (tree_style['space'] if i == len(children) - 1 else tree_style['branch_vertical'])
        child_dialogue = extract_dialogue_structure(child, level + 1, random_selection_level, tree_counter, branch_counter, new_prefix)
        if child_dialogue:
            dialogue.extend(child_dialogue)
            if txt_type == 'full' and random_selection_level >= 2 and level < random_selection_level and p_tags_indices:
                for idx in p_tags_indices:
                    current_level, level_str, text, classes, tree_prefix, tree_counter, branch_counter = dialogue[idx]
                    dialogue[idx] = (current_level, f"{level_str} (↓)", text, classes, tree_prefix, tree_counter, branch_counter)
            p_tags_indices = []
        else:
            if last_h1 is not None:
                current_level, level_str, text, classes, tree_prefix, tree_counter, branch_counter = dialogue[last_h1]
                if txt_type == 'full' and random_selection_level >= 2:
                    dialogue[last_h1] = (current_level, f"{level_str} (✕)", text, classes, tree_prefix, tree_counter, branch_counter)
                last_h1 = None
            for idx in p_tags_indices:
                current_level, level_str, text, classes, tree_prefix, tree_counter, branch_counter = dialogue[idx]
                if txt_type == 'full' and random_selection_level >= 2:
                    dialogue[idx] = (current_level, f"{level_str} (✕)", text, classes, tree_prefix, tree_counter, branch_counter)
            p_tags_indices = []
    return dialogue

def extract_text_from_html(html_content, random_selection_level):
    soup = BeautifulSoup(html_content, 'html.parser')
    headers = soup.find_all('div', {'data-role': 'header'})
    script_tag = soup.find('script', string=re.compile('textarr='))
    if script_tag:
        text_array_match = re.search(r'textarr=\[(.*?)\];', script_tag.string, re.DOTALL)
        id_array_match = re.search(r'inarr=\[(.*?)\];', script_tag.string, re.DOTALL)
        if text_array_match and id_array_match:
            text_array_string = text_array_match.group(1)
            id_array_string = id_array_match.group(1)
            text_array = eval('[' + text_array_string + ']')
            id_array = eval('[' + id_array_string + ']')
            text_dict = {str(id_val): text for id_val, text in zip(id_array, text_array)}
            dialogue_text = []
            tree_counter = 0
            for header in headers:
                tree_counter += 1
                header_text = header.find('h1').text.strip()
                main_content = header.find_next_sibling('div', {'data-role': 'main'})
                dialogue_structure = extract_dialogue_structure(main_content, random_selection_level=random_selection_level, tree_counter=tree_counter)
                current_branch = []
                last_branch_counter = 0
                for i, (level, level_str, text, text_classes, tree_prefix, tree_counter, branch_counter) in enumerate(dialogue_structure):
                    if level == 1 and branch_counter != last_branch_counter:
                        if current_branch:
                            if tree_style == ASCII_TREE:
                                current_branch[-1] = tree_style['root_closing'] + current_branch[-1][4:]
                            dialogue_text.extend(current_branch)
                            current_branch = []
                        current_branch.append(f"\n{'*' * 20}\n{LANG[current_lang]['tree']} {tree_counter} - {LANG[current_lang]['branch']} {branch_counter}\n{header_text}\n{'*' * 20}")
                        last_branch_counter = branch_counter
                    for text_class in text_classes:
                        if text_class in text_dict:
                            if txt_type == 'full':
                                line = f"{tree_prefix}{level_str} {text_dict[text_class]}"
                            else:
                                line = f"{tree_prefix}{text_dict[text_class]}"
                            if tree_style == ASCII_TREE:
                                if level > 1:
                                    line = tree_style['root_vertical'] + line[4:]
                            else:
                                line = tree_style['space'] * (level - 1) + line.lstrip()
                            current_branch.append(line)
                if current_branch:
                    if tree_style == ASCII_TREE:
                        current_branch[-1] = tree_style['root_closing'] + current_branch[-1][4:]
                    dialogue_text.extend(current_branch)
            return dialogue_text
    return []

def process_html_files(directory, random_selection_level):
    print(LANG[current_lang]['processing_started'])
    processed_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            print(LANG[current_lang]['processing_file'].format(filename))
            html_path = os.path.join(directory, filename)
            txt_path = os.path.splitext(html_path)[0] + '.txt'
            with open(html_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            extracted_text = extract_text_from_html(html_content, random_selection_level)
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                for line in extracted_text:
                    txt_file.write(line + '\n')
            processed_files.append(os.path.basename(txt_path))
            print(LANG[current_lang]['finished_file'].format(filename, os.path.basename(txt_path)))
    return processed_files

def list_processed_files(processed_files):
    print(LANG[current_lang]['list_processed'])
    if processed_files:
        for file in processed_files:
            print(f"- {file}")
    else:
        print(LANG[current_lang]['no_files_processed'])

def get_user_input():
    while True:
        try:
            level = int(input(LANG[current_lang]['input_level']))
            if level < 0:
                print(LANG[current_lang]['invalid_input'])
            else:
                return level
        except ValueError:
            print(LANG[current_lang]['invalid_input'])

def choose_language():
    global current_lang
    while True:
        lang = input(LANG['ru']['choose_language']).lower()
        if lang in ['en', 'ru']:
            current_lang = lang
            break
        else:
            print(LANG['en']['invalid_choice'])
            print(LANG['ru']['invalid_choice'])

def choose_txt_type():
    global txt_type
    while True:
        choice = input(LANG[current_lang]['choose_txt_type']).lower()
        if choice in ['full', 'simple']:
            txt_type = choice
            break
        else:
            print(LANG[current_lang]['invalid_txt_choice'])

def main():
    global current_lang, txt_type, tree_style
    choose_language()
    current_directory = os.path.dirname(os.path.abspath(__file__))

    choose_txt_type()
    choose_tree_style()
    random_selection_level = get_user_input()

    while True:
        try:
            processed_files = process_html_files(current_directory, random_selection_level)
            print(LANG[current_lang]['processing_completed'])
            list_processed_files(processed_files)
            print(LANG[current_lang]['total_processed'].format(len(processed_files)))
        except Exception as e:
            print(LANG[current_lang]['error_processing'].format(str(e)))

        print(LANG[current_lang]['script_completed'])

        while True:
            try:
                choice = input(LANG[current_lang]['press_enter']).lower()
                if choice == '':
                    print(LANG[current_lang]['restarting'])
                    break
                elif choice == 'r':
                    print(LANG[current_lang]['changing_settings'])
                    choose_txt_type()
                    choose_tree_style()
                    random_selection_level = get_user_input()
                    break
                elif choice == 'q':
                    print(LANG[current_lang]['quitting'])
                    return
                else:
                    print(LANG[current_lang]['invalid_restart_choice'])
            except KeyboardInterrupt:
                print(LANG[current_lang]['quitting'])
                return

if __name__ == "__main__":
    main()