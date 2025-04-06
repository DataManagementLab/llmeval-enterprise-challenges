import logging
import os
import shutil

from llms4de.data import get_data_path, dump_json, load_json, dump_str, load_str, download_url, get_task_dir, \
    get_download_dir, get_instances_dir, get_requests_dir, get_responses_dir, get_predictions_dir, get_results_dir

logger = logging.getLogger(__name__)


def test_get_data_path() -> None:
    assert get_data_path().is_dir()


def test_pipeline_dirs() -> None:
    t = get_data_path() / "my-task"
    p = get_task_dir("my-task")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/download"
    p = get_download_dir("my-task", "my-dataset")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/experiments/my-experiment/instances"
    p = get_instances_dir("my-task", "my-dataset", "my-experiment")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/experiments/my-experiment/requests"
    p = get_requests_dir("my-task", "my-dataset", "my-experiment")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/experiments/my-experiment/responses"
    p = get_responses_dir("my-task", "my-dataset", "my-experiment")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/experiments/my-experiment/predictions"
    p = get_predictions_dir("my-task", "my-dataset", "my-experiment")
    assert t.is_dir()
    assert p == t

    t = get_data_path() / "my-task/my-dataset/experiments/my-experiment/results"
    p = get_results_dir("my-task", "my-dataset", "my-experiment")
    assert t.is_dir()
    assert p == t

    f = t / "test.txt"
    with open(f, "w", encoding="utf-8") as file:
        file.write("test")
    _ = get_results_dir("my-task", "my-dataset", "my-experiment", clear=True)
    assert not f.is_file()

    shutil.rmtree(get_data_path() / "my-task")


def test_dump_json_and_load_json() -> None:
    path = get_data_path() / "tmp_test.json"
    dump_json({"key": "value"}, path)
    assert load_json(path) == {"key": "value"}
    os.remove(path)


def test_dump_str_and_load_str() -> None:
    path = get_data_path() / "tmp_test.txt"
    dump_str("test", path)
    assert load_str(path) == "test"
    os.remove(path)


def test_download_url() -> None:
    # without unzipping
    url = "https://github.com/DataManagementLab/llmeval-tada24/archive/refs/heads/main.zip"
    path = get_data_path() / "tmp_download.zip"
    download_url(url, path)
    assert path.is_file()
    os.remove(path)

    # with unzipping
    path = get_data_path() / "tmp_download"
    download_url(url, path, unzip=True)
    assert path.is_dir()
    shutil.rmtree(path)

    # with untaring (this runs too long...)
    # url = "https://fm-data-tasks.s3.us-west-1.amazonaws.com/datasets.tar.gz"
    # path = get_data_path() / "tmp_download"
    # download_url(url, path, untar=True)
    # assert path.is_dir()
    # shutil.rmtree(path)
