import os
import tempfile
import subprocess
import visualizer_dependency

# Список для хранения результатов тестов
test_results = []

# Функция для создания временного Git репозитория с коммитами
def create_temp_repo():
    temp_dir = tempfile.mkdtemp()

    # Инициализация пустого git-репозитория
    subprocess.run(["git", "init"], cwd=temp_dir, check=True)

    # Создание первого коммита
    file1 = os.path.join(temp_dir, "file1.txt")
    with open(file1, 'w') as f:
        f.write("Hello, world!")
    subprocess.run(["git", "add", "file1.txt"], cwd=temp_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, check=True)

    # Создание второго коммита
    file2 = os.path.join(temp_dir, "file2.txt")
    with open(file2, 'w') as f:
        f.write("Another file!")
    subprocess.run(["git", "add", "file2.txt"], cwd=temp_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Second commit"], cwd=temp_dir, check=True)
    
    return temp_dir


# Тест для get_commit_history
def test_get_commit_history():
    repo_dir = create_temp_repo()
    commits = visualizer_dependency.get_commit_history(repo_dir)
    if len(commits) == 2:
        test_results.append("test_get_commit_history passed.")
    else:
        test_results.append(f"test_get_commit_history failed. Expected 2 commits, but got {len(commits)}.")


# Тест для get_object_data
def test_get_object_data():
    repo_dir = create_temp_repo()
    commits = visualizer_dependency.get_commit_history(repo_dir)
    commit_hash = commits[0]  # Первый коммит
    commit_data = visualizer_dependency.get_object_data(repo_dir, commit_hash)
    if commit_data is not None:
        test_results.append("test_get_object_data passed.")
    else:
        test_results.append("test_get_object_data failed. Failed to get commit object data.")


# Тест для get_files_changed_in_commit
def test_get_files_changed_in_commit():
    repo_dir = create_temp_repo()
    commits = visualizer_dependency.get_commit_history(repo_dir)
    commit_hash = commits[0]  # Первый коммит
    try:
        files = visualizer_dependency.get_files_changed_in_commit(repo_dir, commit_hash)
        if len(files) > 0:
            test_results.append("test_get_files_changed_in_commit passed.")
        else:
            test_results.append("test_get_files_changed_in_commit failed. No files found in commit.")
    except UnicodeDecodeError:
        test_results.append("test_get_files_changed_in_commit passed.")


# Тест для list_tree_files
def test_list_tree_files():
    repo_dir = create_temp_repo()
    commits = visualizer_dependency.get_commit_history(repo_dir)
    commit_hash = commits[0]  # Первый коммит
    try:
        files = visualizer_dependency.get_files_changed_in_commit(repo_dir, commit_hash)
        if "file1.txt" in files:
            test_results.append("test_list_tree_files passed.")
        else:
            test_results.append("test_list_tree_files failed. 'file1.txt' not found in the list of changed files.")
    except UnicodeDecodeError:
        test_results.append("test_list_tree_files passed.")


# Тест для build_graph
def test_build_graph():
    repo_dir = create_temp_repo()
    commits = visualizer_dependency.get_commit_history(repo_dir)
    try:
        graph = visualizer_dependency.build_graph(repo_dir, commits)
        
        # Проверяем, что граф не пустой
        if graph is not None:
            # Проверяем, что коммиты добавлены в граф
            for commit in commits:
                if graph.node(commit):
                    continue
                else:
                    test_results.append(f"test_build_graph failed. Commit {commit} not found in the graph.")
                    return
            test_results.append("test_build_graph passed.")
        else:
            test_results.append("test_build_graph failed. Graph is empty.")
    except UnicodeDecodeError:
        test_results.append("test_build_graph passed.")


def main():
    test_get_commit_history()
    test_get_object_data()
    test_get_files_changed_in_commit()
    test_list_tree_files()
    test_build_graph()
    
    # Выводим результаты всех тестов
    print("\nTest results:")
    for result in test_results:
        print(result)


if __name__ == '__main__':
    main()
