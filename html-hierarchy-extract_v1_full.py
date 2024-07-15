import os
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple

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

LANG: Dict[str, Dict[str, str]] = {
    'en': {
        'choose_language': "Choose language (en/ru, lowercase): ",
        'invalid_choice': "Invalid choice. Please enter 'en' for English or 'ru' for Russian (lowercase).",
        'choose_tree_style': """\n\n--- START OF THE ENTRY ---\n\n\nThis script is designed to extract data from HTML files while preserving its hierarchical structure. The script primarily searches for the class attribute within <h1> heading tags (e.g., <h1 class="###">#.</h1>). However, if the <h1> tag lacks a class attribute (e.g., <h1>#.Character, # replies</h1>), the script then searches for class attributes within nearby <p> paragraph tags (e.g., <p class="###">#.</p><p class="###">#). The extracted class number is then matched with identifiers provided in the inarr= parameter, and the corresponding text from the textarr= parameter is retrieved based on the found identifiers. The output file follows this format:\n\n********************\nTREE 1 - BRANCH 1\nHero and Character\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n┃   │   └── [№03-h01-ID] Character: line...\n┃   │       ├── [№04-p01-ID] (↓) Hero: reply, leads to the same line...\n┃   │       └── [№04-p02-ID] (↓) Hero: reply, leads to the same line...\n┃   │           └── [№05-h01-ID] Character: line...\n┃   │               ├── [№06-p01-ID] (X) Hero: reply, ends the dialogue...\n┃   │               └── [№06-p02-ID] (X) Hero: reply, ends the dialogue...\n┃   └── [№02-h02-ID] Hero: reply...\n┃       └── [№03-h01-ID] Character: line...\n┃           └── [№04-h01-ID] Hero: reply...\n┃               └── [№05-h01-ID] Character: line...\n┃                   ├── [№06-p01-ID] (↓) Hero: reply, leads to the same line...\n┃                   └── [№06-p02-ID] (↓) Hero: reply, leads to the same line...\n┃                       └── [№07-h01-ID] Character: line...\n┃                           ├── [№08-p01-ID] (X) Hero: reply, ends the dialogue...\n┗━━                         └── [№08-p02-ID] (X) Hero: reply, ends the dialogue...\n\n********************\nTREE 1 - BRANCH 2\nHero and Character\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n\n********************\nTREE 2 - BRANCH 1\nHero and Character, Day #\n********************\n┏━━ [№01-h01-ID] Character: line...\n┃   ├── [№02-h01-ID] Hero: reply...\n\n"TREE #":  Indicates the start of a new header (e.g., <div data-role="header"> <h1>Haruspex & Peter Stamatin</h1>). The number increments with each header found.\n"BRANCH #": Indicates the start of a new dialogue. The number increments with each new dialogue within the current tree.\n"Hero and Character": Text extracted from the header (e.g., <div data-role="header"> <h1>Haruspex & Peter Stamatin</h1>).\n"№##": Displays the level of depth in the hierarchy.\n"h/p##": Displays the sequence number of the <h1> or <p> tag at the current level.\n"ID": The number extracted from the class= attribute. Corresponds to strings IDs in main.dat of Pathologic Alpha / 2005 / Classic. In Pathologic 2, the situation is more complex.\n"(↓)": Indicates that all replies lead to the same line located one level below. Used only for <p> tags, which are only extracted if the structure <h1>#.Character, # replies</h1><p class="###">#.</p><p class="###"># is present.\n"(X)": Indicates that the current level has no children (in the game, such a reply should end the dialogue).\n\n\n--- END OF THE ENTRY ---\n\n\nTwo options are available for visualizing the tree structure: using ASCII characters or indentation.\n\n- ASCII Representation: This option employs ASCII characters to depict the tree structure.\n\n┏━━ [№01-h01-ID] Character: Dialogue...\n┃   ├── [№02-h01-ID] Hero: Response...\n┃   │   └── [№03-h01-ID] Character: Dialogue...\n┃   │       ├── [№04-p01-ID] (X) Hero: Dialogue-ending response...\n┃   │       └── [№04-p02-ID] (X) Hero: Dialogue-ending response...\n┗━━ └── [№02-h02-ID] (X) Hero: Dialogue-ending response...\n\n- Indentation Representation: This option utilizes spaces to create indentations that represent the tree structure.\n\n[№01-h01-ID] Character: Dialogue...\n [№02-h01-ID] Hero: Response...\n   [№03-h01-ID] Character: Dialogue...\n     [№04-p01-ID] (X) Hero: Dialogue-ending response...\n     [№04-p02-ID] (X) Hero: Dialogue-ending response...\n [№02-h02-ID] (X) Hero: Dialogue-ending response...\n\nYour choice (ascii/indent, lowercase): """,
        'invalid_tree_choice': "Invalid choice. Please enter 'ascii' or 'indent' (all lowercase).",
        'restart_prompt': "Press ENTER to run the script again, R to change settings, or Q to quit: ",
        'invalid_restart_choice': "Invalid choice. Press ENTER to run the script again, R to change settings, or Q to quit.",
        'changing_settings': "Changing settings...",
        'quitting': "Quitting the script...",
        'restarting': "Restarting the script...",
        'processing_started': "\nStarting HTML file processing",
        'processing_completed': "HTML file processing completed successfully",
        'files_processed': "Total files processed: {}",
        'error_occurred': "An error occurred while processing files: {}",
        'script_execution_completed': "Script execution completed",
        'file_processing_start': "Processing file: {}",
        'file_processed': "Processed {} → {}",
        'all_files_processed': "Finished processing all HTML files in the directory",
        'processed_files_list': "List of all processed files:",
        'no_files_processed': "No files were processed.",
        'tree': "TREE",
        'branch': "BRANCH",
    },
    'ru': {
        'choose_language': "Выберите язык (en/ru, нижний регистр): ",
        'invalid_choice': "Неверный выбор. Введите 'en' для английского или 'ru' для русского языка (нижний регистр).",
        'choose_tree_style': """\n\n-- НАЧАЛО ВСТУПЛЕНИЯ ---\n\n\nДанный скрипт предназначен для извлечения данных из HTML-файлов с сохранением их иерархической структуры. Скрипт в первую очередь ищет атрибут class внутри тегов заголовков <h1> (<h1 class="###">#.</h1>), но если у тега <h1> отсутствует атрибут class (например, <h1>#.Персонаж, # реплики</h1>),  осуществляет поиск атрибутов class у ближайших тегов параграфов <p> (<p class="###">#.</p><p class="###">#). Номер класса сопоставляется с идентификаторами, предоставленными в параметре inarr=, а из параметра textarr= извлекается текст, соответствующий найденным идентификаторам. Выходной файл имеет следующий формат:\n\n********************\nДРЕВО 1 - ВЕТВЬ 1\nГерой и Персонаж\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n┃   │   └── [№03-h01-ID] Персонаж: реплика...\n┃   │       ├── [№04-p01-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃   │       └── [№04-p02-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃   │           └── [№05-h01-ID] Персонаж: реплика...\n┃   │               ├── [№06-p01-ID] (X) Герой: ответ, завершает диалог...\n┃   │               └── [№06-p02-ID] (X) Герой: ответ, завершает диалог...\n┃   └── [№02-h02-ID] Герой: ответ...\n┃       └── [№03-h01-ID] Персонаж: реплика...\n┃           └── [№04-h01-ID] Герой: ответ...\n┃               └── [№05-h01-ID] Персонаж: реплика...\n┃                   ├── [№06-p01-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃                   └── [№06-p02-ID] (↓) Герой: ответ, ведет к той же реплике...\n┃                       └── [№07-h01-ID] Персонаж: реплика...\n┃                           ├── [№08-p01-ID] (X) Герой: ответ, завершает диалог...\n┗━━                         └── [№08-p02-ID] (X) Герой: ответ, завершает диалог...\n\n********************\nДРЕВО 1 - ВЕТВЬ 2\nГерой и Персонаж\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n\n********************\nДРЕВО 2 - ВЕТВЬ 1\nГерой и Персонаж, День #\n********************\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n\n"ДРЕВО #": Обозначает начало нового заголовка (например, <div data-role="header"> <h1>Гаруспик & Петр Стаматин</h1>). Номер увеличивается с каждым найденным заголовком.\n"ВЕТВЬ #": Обозначает начало нового диалога. Номер увеличивается с каждым новым диалогом в рамках текущего дерева.\n"Герой и Персонаж": Текст, извлеченный из заголовка (например, <div data-role="header"> <h1>Гаруспик & Петр Стаматин</h1>).\n"№##":  Отображает уровень погружения в иерархию.\n"h/p##":  Отображает порядковый номер тега <h1> или <p> на текущем уровне.\n"ID":  Номер, извлеченный из атрибута class=. Соответствует strings ID в main.dat Pathologic Alpha / 2005 / Classic. В Pathologic 2 ситуация сложнее.\n"(↓)": Указывает, что все ответы ведут к одной и той же реплике, расположенной на уровень ниже. Используется только для тегов <p>, которые извлекаются только при наличии структуры <h1>#.Персонаж, # реплик</h1><p class="###">#.</p><p class="###">#.\n"(X)":  Указывает, что текущий уровень не имеет дочерних элементов (в игре такой ответ должен завершать диалог).\n\n\n-- КОНЕЦ ВСТУПЛЕНИЯ ---\n\n\nПредлагается два варианта отображения древовидной структуры: с использованием ASCII-символов и с использованием отступов.\n- ASCII: В данном варианте структура дерева отображается с помощью символов ASCII.\n\n┏━━ [№01-h01-ID] Персонаж: реплика...\n┃   ├── [№02-h01-ID] Герой: ответ...\n┃   │   └── [№03-h01-ID] Персонаж: реплика...\n┃   │       ├── [№04-p01-ID] (X) Герой: ответ, завершающий диалог...\n┃   │       └── [№04-p02-ID] (X) Герой: ответ, завершающий диалог...\n┗━━ └── [№02-h02-ID] (X) Герой: ответ, завершающий диалог...\n\n- Отступы: В данном варианте структура дерева отображается с помощью пробелов, формирующих отступы.\n\n[№01-h01-ID] Персонаж: реплика...\n [№02-h01-ID] Герой: ответ...\n   [№03-h01-ID] Персонаж: реплика...\n     [№04-p01-ID] (X) Герой: ответ, завершающий диалог...\n     [№04-p02-ID] (X) Герой: ответ, завершающий диалог...\n [№02-h02-ID] (X) Герой: ответ, завершающий диалог...\n\nВаш выбор (ascii/indent, нижний регистр): """,
        'invalid_tree_choice': "Неверный выбор. Введите 'ascii' или 'indent' (нижний регистр).",
        'restart_prompt': "Нажмите ENTER, чтобы запустить скрипт снова, R для изменения настроек или Q для выхода: ",
        'invalid_restart_choice': "Неверный выбор. Нажмите ENTER, чтобы запустить скрипт снова, R для изменения настроек или Q для выхода.",
        'changing_settings': "Изменение настроек...",
        'quitting': "Завершение работы скрипта...",
        'restarting': "Перезапуск скрипта...",
        'processing_started': "\nНачало обработки HTML-файлов",
        'processing_completed': "Обработка HTML-файлов успешно завершена",
        'files_processed': "Всего обработано файлов: {}",
        'error_occurred': "Произошла ошибка при обработке файлов: {}",
        'script_execution_completed': "Выполнение скрипта завершено",
        'file_processing_start': "Обработка файла: {}",
        'file_processed': "Обработан {} → {}",
        'all_files_processed': "Обработка всех HTML-файлов в директории завершена",
        'processed_files_list': "Список всех обработанных файлов:",
        'no_files_processed': "Файлы не были обработаны.",
        'tree': "ДРЕВО",
        'branch': "ВЕТВЬ",
    }
}

current_lang: str = 'en'
tree_style: Dict[str, str] = ASCII_TREE

def choose_language():
    global current_lang
    while True:
        lang = input(LANG['en']['choose_language']).lower()
        if lang in LANG:
            current_lang = lang
            break
        print(LANG['en']['invalid_choice'])
        print(LANG['ru']['invalid_choice'])

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
        print(LANG[current_lang]['invalid_tree_choice'])

def extract_dialogue_structure(element, level: int = 0, tree_counter: int = 1, branch_counter: int = 1, prefix: str = '') -> List[Tuple[int, str, str, List[str]]]:
    dialogue = []
    level_counter: Dict[int, int] = {}
    p_counter: Dict[int, Dict[str, int]] = {}
    last_h1 = None
    p_tags_indices = []

    children = list(element.children)
    for i, child in enumerate(children):
        if child.name == 'div' and child.get('data-role') == 'collapsible':
            h1_tags = child.find_all('h1', recursive=False)
            for h1_tag in h1_tags:
                class_number = h1_tag.get('class', [[]])[0]
                current_level = int(re.match(r'(\d+)', h1_tag.text.strip()).group(1) or level + 1)

                if current_level == 1:
                    level_counter.clear()
                    p_counter.clear()
                    branch_counter += 1

                level_counter[current_level] = level_counter.get(current_level, 0) + 1

                if h1_tag.get('class'):
                    level_str = f"[№{current_level:02d}-h{level_counter[current_level]:02d}-{class_number}]"
                    tree_prefix = tree_style['root_opening'] if current_level == 1 else prefix + (tree_style['branch_closing'] if i == len(children) - 1 else tree_style['branch_branch'])
                    dialogue.append((current_level, f"{tree_prefix}{level_str}", h1_tag.text.strip(), h1_tag.get('class')))
                    last_h1 = len(dialogue) - 1
                else:
                    p_tags = child.find_all('p', class_=True, recursive=False)
                    p_tags_indices = []
                    for j, p_tag in enumerate(p_tags):
                        p_level = p_counter.setdefault(current_level, {'level': current_level * 1, 'count': 0})
                        p_level['count'] += 1
                        class_number = p_tag.get('class')[0]
                        level_str = f"[№{p_level['level']:02d}-p{p_level['count']:02d}-{class_number}]"
                        tree_prefix = prefix + (tree_style['branch_closing'] if i == len(children) - 1 and j == len(p_tags) - 1 else tree_style['branch_branch'])
                        dialogue.append((p_level['level'], f"{tree_prefix}{level_str}", p_tag.text.strip(), p_tag.get('class')))
                        p_tags_indices.append(len(dialogue) - 1)

            child_prefix = prefix + (tree_style['space'] if i == len(children) - 1 else tree_style['branch_vertical'])
            child_dialogue = extract_dialogue_structure(child, level + 1, tree_counter, branch_counter, child_prefix)
            
            if child_dialogue:
                dialogue.extend(child_dialogue)
                if p_tags_indices:
                    for idx in p_tags_indices:
                        current_level, level_str, text, classes = dialogue[idx]
                        dialogue[idx] = (current_level, f"{level_str} (↓)", text, classes)
            else:
                for idx in p_tags_indices:
                    current_level, level_str, text, classes = dialogue[idx]
                    dialogue[idx] = (current_level, f"{level_str} (X)", text, classes)
            
            p_tags_indices.clear()

            if last_h1 is not None and not child_dialogue:
                current_level, level_str, text, classes = dialogue[last_h1]
                dialogue[last_h1] = (current_level, f"{level_str} (X)", text, classes)
                last_h1 = None

    return dialogue

def extract_text_from_html(html_content: str) -> List[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    headers = soup.find_all('div', {'data-role': 'header'})
    script_tag = soup.find('script', string=re.compile('textarr='))
    
    if script_tag:
        text_array_match = re.search(r'textarr=\[(.*?)\];', script_tag.string, re.DOTALL)
        id_array_match = re.search(r'inarr=\[(.*?)\];', script_tag.string, re.DOTALL)
        
        if text_array_match and id_array_match:
            text_array = eval('[' + text_array_match.group(1) + ']')
            id_array = eval('[' + id_array_match.group(1) + ']')
            text_dict = dict(zip(map(str, id_array), text_array))
            
            dialogue_text = []
            for tree_counter, header in enumerate(headers, 1):
                header_text = header.find('h1').text.strip()
                main_content = header.find_next_sibling('div', {'data-role': 'main'})
                dialogue_structure = extract_dialogue_structure(main_content, tree_counter=tree_counter)
                
                current_branch = []
                branch_counter = 0
                for level, level_str, text, text_classes in dialogue_structure:
                    if level == 1:
                        if current_branch:
                            if tree_style == ASCII_TREE:
                                current_branch[-1] = tree_style['root_closing'] + current_branch[-1][4:]
                            dialogue_text.extend(current_branch)
                            current_branch.clear()
                        branch_counter += 1
                        current_branch.append(f"\n{'*' * 20}\n{LANG[current_lang]['tree']} {tree_counter} - {LANG[current_lang]['branch']} {branch_counter}\n{header_text}\n{'*' * 20}")
                    
                    for text_class in text_classes:
                        if text_class in text_dict:
                            line = f"{level_str} {text_dict[text_class]}"
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

def process_html_files(directory: str) -> List[str]:
    print(LANG[current_lang]['processing_started'])
    processed_files = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            html_path = os.path.join(directory, filename)
            txt_path = os.path.splitext(html_path)[0] + '.txt'
            print(LANG[current_lang]['file_processing_start'].format(filename))
            
            with open(html_path, 'r', encoding='utf-8') as html_file:
                html_content = html_file.read()
            
            extracted_text = extract_text_from_html(html_content)
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write('\n'.join(extracted_text))
            
            print(LANG[current_lang]['file_processed'].format(filename, os.path.basename(txt_path)))
            processed_files.append(os.path.basename(txt_path))
    
    print(LANG[current_lang]['all_files_processed'])
    return processed_files

def list_processed_files(processed_files: List[str]):
    print(LANG[current_lang]['processed_files_list'])
    if processed_files:
        for file in processed_files:
            print(f"- {file}")
    else:
        print(LANG[current_lang]['no_files_processed'])

def main():
    choose_language()
    choose_tree_style()

    while True:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            processed_files = process_html_files(current_directory)
            print(LANG[current_lang]['processing_completed'])
            list_processed_files(processed_files)
            print(LANG[current_lang]['files_processed'].format(len(processed_files)))
        except Exception as e:
            print(LANG[current_lang]['error_occurred'].format(str(e)))

        print(LANG[current_lang]['script_execution_completed'])

        while True:
            try:
                choice = input(LANG[current_lang]['restart_prompt']).lower()
                if choice == '':
                    print(LANG[current_lang]['restarting'])
                    break
                elif choice == 'r':
                    print(LANG[current_lang]['changing_settings'])
                    choose_tree_style()
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