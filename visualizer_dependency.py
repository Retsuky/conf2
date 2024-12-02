import os
import sys
import subprocess
import graphviz
import argparse


def get_commit_history(repo_path):
    """
    Возвращает список хешей коммитов для репозитория.
    Используется команда git rev-list для получения истории.
    """
    try:
        # Выполняем git rev-list для получения всех коммитов
        result = subprocess.run(
            ['git', 'rev-list', '--all'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.splitlines()
        commits.sort()  # Сортировка по хешу, можно улучшить на основе времени
        return commits
    except subprocess.CalledProcessError:
        print("Error: Unable to get commits from the repository.")
        sys.exit(1)


def get_files_changed_in_commit(repo_path, commit_hash):
    """
    Получает список измененных файлов для заданного коммита
    с помощью git diff.
    """
    try:
        # Выполняем git diff-tree для получения измененных файлов
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        files_changed = result.stdout.splitlines()
        return files_changed
    except subprocess.CalledProcessError:
        print(f"Error: Unable to get files for commit {commit_hash}.")
        return []


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
        graph.edge(commits[i-1], commits[i])  # Добавление ребра от предыдущего коммита к текущему

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
