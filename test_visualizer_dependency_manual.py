import os
import shutil
from visualizer_dependency import get_git_log, get_commit_files, build_dependency_graph

def remove_readonly(func, path, exc_info):
    """Сбрасывает атрибут "только чтение" и повторяет удаление."""
    os.chmod(path, 0o777)
    func(path)

def setup_fake_repo():
    """Создаёт фиктивный Git-репозиторий для тестов."""
    repo_path = "./fake_repo"
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, onerror=remove_readonly)  # Удаление с обработкой ошибок доступа
    os.makedirs(repo_path)
    os.system(f"git -C {repo_path} init")
    # Создаём файлы
    with open(os.path.join(repo_path, "file1.txt"), "w") as f:
        f.write("Content of file1")
    os.system(f"git -C {repo_path} add .")
    os.system(f"git -C {repo_path} commit -m \"Initial commit\"")  # Убраны лишние символы
    with open(os.path.join(repo_path, "file2.txt"), "w") as f:
        f.write("Content of file2")
    os.system(f"git -C {repo_path} add .")
    os.system(f"git -C {repo_path} commit -m \"Second commit\"")  # Убраны лишние символы
    return repo_path

def test_get_git_log():
    """Тест функции get_git_log."""
    repo_path = setup_fake_repo()
    try:
        log = get_git_log(repo_path)
        assert len(log) == 2, f"Ожидалось 2 коммита, получено: {len(log)}"
        print("test_get_git_log: OK")
    except Exception as e:
        print(f"test_get_git_log: FAILED ({e})")

def test_get_commit_files():
    """Тест функции get_commit_files."""
    repo_path = setup_fake_repo()
    try:
        # Получаем хэш последнего коммита
        log = get_git_log(repo_path)
        commit_hash = log[0].split()[0]
        files = get_commit_files(repo_path, commit_hash)
        assert "file2.txt" in files, f"Ожидалось 'file2.txt', получено: {files}"
        print("test_get_commit_files: OK")
    except Exception as e:
        print(f"test_get_commit_files: FAILED ({e})")

def test_build_dependency_graph():
    """Тест функции build_dependency_graph."""
    repo_path = setup_fake_repo()
    try:
        graph = build_dependency_graph(repo_path)
        # Сохранение графа в файл
        output_path = "./test_graph"
        graph.render(output_path, cleanup=True)  # Сохранение в test_graph.png
        print(f"Граф сохранён как {output_path}.png")
        print("test_build_dependency_graph: OK")
    except Exception as e:
        print(f"test_build_dependency_graph: FAILED ({e})")

if __name__ == "__main__":
    test_get_git_log()
    test_get_commit_files()
    test_build_dependency_graph()
