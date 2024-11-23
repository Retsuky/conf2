import os
import subprocess
import argparse
from graphviz import Digraph

def get_git_log(repo_path):
    """Получить список коммитов и их родителей."""
    cmd = ['git', '-C', repo_path, 'log', '--pretty=format:%H %P']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    return result.stdout.strip().split('\n')

def get_commit_files(repo_path, commit_hash):
    """Получить файлы и папки, затронутые коммитом."""
    cmd = ['git', '-C', repo_path, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    files = result.stdout.strip().split('\n')
    return files

def build_dependency_graph(repo_path):
    """Создать граф зависимостей."""
    log = get_git_log(repo_path)
    graph = Digraph(format='png')
    for line in log:
        parts = line.split()
        commit_hash = parts[0]
        parents = parts[1:]
        files = get_commit_files(repo_path, commit_hash)
        label = f"{commit_hash[:7]}\\n" + "\\n".join(files[:5])  # Отображаем только первые 5 файлов
        if len(files) > 5:
            label += "\\n..."
        graph.node(commit_hash, label=label)
        for parent in parents:
            graph.edge(parent, commit_hash)
    return graph

def main():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей для Git-репозитория.")
    parser.add_argument('--graphviz-path', type=str, required=True, help="Путь к программе Graphviz (например, dot).")
    parser.add_argument('--repo-path', type=str, required=True, help="Путь к анализируемому Git-репозиторию.")
    parser.add_argument('--output-path', type=str, required=True, help="Путь для сохранения файла изображения графа.")
    args = parser.parse_args()

    # Проверка репозитория
    if not os.path.isdir(args.repo_path) or not os.path.isdir(os.path.join(args.repo_path, '.git')):
        print(f"Ошибка: Путь {args.repo_path} не является Git-репозиторием.")
        return

    # Создание графа
    try:
        graph = build_dependency_graph(args.repo_path)
        graph.render(args.output_path, cleanup=True)
        print(f"Граф зависимостей успешно сохранен в файл: {args.output_path}.png")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
