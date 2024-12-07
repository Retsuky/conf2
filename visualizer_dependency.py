import os
import sys
import graphviz
import argparse
import zlib
import re


def get_commit_history(repo_path):
    """
    Возвращает список хешей коммитов для репозитория через чтение файлов refs.
    """
    heads_path = os.path.join(repo_path, ".git", "refs", "heads", "main")
    
    if not os.path.exists(heads_path):
        print(f"Error: Branch 'main' not found in repository at {repo_path}")
        sys.exit(1)

    with open(heads_path, "r") as file:
        commit_hash = file.read().strip()

    # Получаем всю историю коммитов через цепочку parent
    commits = []
    while commit_hash:
        commits.append(commit_hash)
        commit_data = get_object_data(repo_path, commit_hash)
        parent_match = re.search(b"parent ([a-f0-9]{40})", commit_data)
        commit_hash = parent_match.group(1).decode() if parent_match else None

    commits.reverse()  # Возвращаем в порядке от старых к новым
    return commits


def get_object_data(repo_path, obj_hash):
    """
    Получает необработанные данные объекта Git через его хеш.
    """
    obj_path = os.path.join(repo_path, ".git", "objects", obj_hash[:2], obj_hash[2:])
    
    if not os.path.exists(obj_path):
        print(f"Error: Object {obj_hash} not found in repository.")
        sys.exit(1)

    with open(obj_path, "rb") as file:
        compressed_data = file.read()
        return zlib.decompress(compressed_data)


def get_files_changed_in_commit(repo_path, commit_hash):
    """
    Получает список измененных файлов из дерева коммита через его содержимое.
    """
    commit_data = get_object_data(repo_path, commit_hash)
    tree_match = re.search(b"tree ([a-f0-9]{40})", commit_data)

    if not tree_match:
        print(f"Error: Tree object not found for commit {commit_hash}.")
        return []

    tree_hash = tree_match.group(1).decode()
    return list_tree_files(repo_path, tree_hash)


def list_tree_files(repo_path, tree_hash):
    """
    Возвращает список всех файлов из указанного дерева.
    """
    tree_data = get_object_data(repo_path, tree_hash)
    files = []
    
    index = 0
    while index < len(tree_data):
        # Извлечение прав, имени файла и хеша
        mode_end = tree_data.find(b' ', index)
        name_end = tree_data.find(b'\x00', mode_end)
        file_name = tree_data[mode_end + 1:name_end].decode()
        obj_hash = tree_data[name_end + 1:name_end + 21].hex()

        files.append(file_name)
        index = name_end + 21

    return files


def build_graph(repo_path, commits):
    """
    Строит граф зависимостей с использованием Graphviz.
    """
    graph = graphviz.Digraph(format='png')

    # Добавление коммитов в граф
    for commit in commits:
        files_changed = get_files_changed_in_commit(repo_path, commit)
        node_label = f"Commit: {commit}\nFiles: {', '.join(files_changed)}"
        graph.node(commit, label=node_label)

    # Добавление зависимостей (если один коммит зависит от другого)
    for i in range(1, len(commits)):
        graph.edge(commits[i - 1], commits[i])

    return graph


def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Dependency Graph Visualizer')
    parser.add_argument('--graphviz-path', required=True, help='Path to Graphviz executable')
    parser.add_argument('--repo-path', required=True, help='Path to Git repository')
    parser.add_argument('--output-path', required=True, help='Path to save the output graph')

    args = parser.parse_args()

    # Путь к репозиторию
    repo_path = args.repo_path
    if not os.path.exists(repo_path):
        print(f"Repository path '{repo_path}' does not exist.")
        sys.exit(1)

    # Получение списка коммитов
    commits = get_commit_history(repo_path)

    if not commits:
        print("No commits found in the repository.")
        sys.exit(1)

    # Построение графа зависимостей
    graph = build_graph(repo_path, commits)

    # Установка пути для Graphviz
    os.environ["PATH"] += os.pathsep + args.graphviz_path

    # Генерация и сохранение графа
    output_image_path = args.output_path
    graph.render(output_image_path, cleanup=True)
    print(f"Dependency graph saved to {output_image_path}.png")


if __name__ == '__main__':
    main()
