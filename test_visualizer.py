import os
import sys
import subprocess
from unittest.mock import MagicMock, patch
import visualizer_dependency

# Тест для функции get_commit_history
def test_get_commit_history():
    repo_path = '/mock/repo'
    
    # Мокаем subprocess.run для get_commit_history
    subprocess.run = MagicMock(return_value=MagicMock(stdout='commit1\ncommit2\ncommit3\n', stderr=''))
    
    # Выполняем тест
    commits = visualizer_dependency.get_commit_history(repo_path)
    
    # Проверяем, что вернулись коммиты
    assert commits == ['commit1', 'commit2', 'commit3'], f"Expected ['commit1', 'commit2', 'commit3'], but got {commits}"

    print("Test passed: get_commit_history works correctly.")


# Тест для обработки ошибки, когда путь репозитория неверен
def test_repo_not_found():
    repo_path = '/wrong/path'
    
    # Мокаем subprocess.run, чтобы не пытаться работать с реальной файловой системой
    original_run = subprocess.run
    subprocess.run = MagicMock(side_effect=FileNotFoundError("Repository path does not exist"))

    try:
        # Пытаемся получить историю коммитов
        visualizer_dependency.get_commit_history(repo_path)
    except SystemExit:
        print("Test passed: Repository not found correctly.")
        return
    except FileNotFoundError as e:
        print(f"Test passed: {str(e)}")
        return
    
    print("Test failed: No error raised for invalid repo path.")
    
    # Восстановление оригинальной функции
    subprocess.run = original_run


# Тест для получения измененных файлов в коммите
def test_get_files_changed_in_commit():
    repo_path = '/mock/repo'
    commit_hash = 'commit1'
    
    # Мокаем subprocess.run для get_files_changed_in_commit
    subprocess.run = MagicMock(return_value=MagicMock(stdout='file1.txt\nfile2.txt\n', stderr=''))
    
    # Выполняем тест
    files_changed = visualizer_dependency.get_files_changed_in_commit(repo_path, commit_hash)
    
    # Проверяем, что файлы были получены
    assert files_changed == ['file1.txt', 'file2.txt'], f"Expected ['file1.txt', 'file2.txt'], but got {files_changed}"

    print("Test passed: get_files_changed_in_commit works correctly.")


# Тест для функции build_graph
def test_build_graph():
    repo_path = '/mock/repo'
    commits = ['commit1', 'commit2']

    # Мокаем вызовы для создания графа
    mock_graph = MagicMock()

    # Мокаем функцию get_files_changed_in_commit, чтобы она возвращала фиктивные файлы
    with patch('visualizer_dependency.get_files_changed_in_commit', return_value=['file1.txt', 'file2.txt']):
        with patch('graphviz.Digraph', return_value=mock_graph):
            visualizer_dependency.build_graph(repo_path, commits)

    # Проверяем, что метод node был вызван дважды для двух коммитов
    assert len(mock_graph.node.call_args_list) == 2, "Expected two calls to node()"

    # Проверяем, что правильная метка передается в node для каждого коммита
    assert mock_graph.node.call_args_list[0][1]['label'] == 'Commit: commit1\nFiles: file1.txt, file2.txt', "Unexpected label for commit1"
    assert mock_graph.node.call_args_list[1][1]['label'] == 'Commit: commit2\nFiles: file1.txt, file2.txt', "Unexpected label for commit2"

    print("Test passed: build_graph works correctly.")


# Тест для случая, когда коммиты не найдены
def test_no_commits_found():
    repo_path = '/mock/repo'

    # Мокаем функцию get_commit_history, чтобы она возвращала пустой список
    with patch('visualizer_dependency.get_commit_history', return_value=[]):
        try:
            # Передаем фальшивые параметры командной строки
            subprocess.run(['python', 'test_visualizer.py', '--graphviz-path', '/mock/graphviz', '--repo-path', repo_path, '--output-path', '/mock/output'])
        except SystemExit as e:
            print(f"Test passed: No SystemExit raised for no commits with exit code {e.code}")
            return
        print("Test failed: No SystemExit raised for no commits.")

# Основная функция тестирования
if __name__ == '__main__':
    test_get_commit_history()
    test_repo_not_found()
    test_get_files_changed_in_commit()
    test_build_graph()
    test_no_commits_found()
