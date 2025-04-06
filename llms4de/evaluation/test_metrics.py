import logging

import pytest

from llms4de.evaluation.metrics import Accuracy, ConfusionMatrix, AccuracyBy, ConfusionMatrixBy, \
    bootstrap_standard_error

logger = logging.getLogger(__name__)


def test_boostrap_standard_error() -> None:
    assert round(bootstrap_standard_error(
        {"correct": 100, "incorrect": 200},
        lambda counts: Accuracy(**counts).accuracy,
        1_000
    ), 2) == 0.03

    assert bootstrap_standard_error(
        {"correct": 0, "incorrect": 1},
        lambda counts: Accuracy(**counts).accuracy,
        1_000
    ) == 0.0

    assert bootstrap_standard_error(
        {"correct": 1, "incorrect": 0},
        lambda counts: Accuracy(**counts).accuracy,
        1_000
    ) == 0.0

    with pytest.raises(AssertionError):
        bootstrap_standard_error(
            {"correct": 0, "incorrect": 0},
            lambda counts: Accuracy(**counts).accuracy,
            1_000
        )


def test_accuracy() -> None:
    assert Accuracy(1, 1).total == 2
    assert Accuracy(1, 1).accuracy == 0.5
    assert round(Accuracy(100, 200).bootstrap_accuracy_standard_error(), 2) == 0.03
    assert Accuracy.empty() == Accuracy(correct=0, incorrect=0)

    acc = Accuracy.empty()
    acc.push(True)
    acc.push(False)
    assert acc == Accuracy(correct=1, incorrect=1)

    with pytest.raises(ZeroDivisionError):
        _ = Accuracy.empty().accuracy

    assert Accuracy(0, 1) + Accuracy(1, 0) == Accuracy(1, 1)
    acc = Accuracy(0, 1)
    acc += Accuracy(1, 0)
    assert acc == Accuracy(1, 1)


def test_accuracy_by() -> None:
    acc_by = AccuracyBy.empty(("a", "b"))

    acc_by.push({"a": 1, "b": 1}, True)
    acc_by.push({"a": 1, "b": 1}, True)
    acc_by.push({"a": 1, "b": 2}, False)
    acc_by.push({"a": 2, "b": 2}, False)
    assert acc_by.all == Accuracy(2, 2)
    assert acc_by.group_by_key("b") == {1: Accuracy(2, 0), 2: Accuracy(0, 2)}
    assert acc_by.group_by_key("b", filter_key_values={"a": 1}) == {1: Accuracy(2, 0), 2: Accuracy(0, 1)}

    with pytest.raises(ValueError):
        _ = acc_by.group_by_key("c")

    acc_by = AccuracyBy.empty(tuple())
    acc_by.push({}, True)
    acc_by.push({}, False)
    assert acc_by.all == Accuracy(1, 1)


def test_confusion_matrix() -> None:
    assert ConfusionMatrix(1, 1, 0, 1).total == 3
    assert ConfusionMatrix(1, 1, 0, 1).precision == 0.5
    assert ConfusionMatrix(1, 1, 0, 1).recall == 0.5
    assert ConfusionMatrix(1, 1, 0, 1).f1_score == 0.5
    assert ConfusionMatrix(1, 1, 1, 1).accuracy == 0.5
    assert ConfusionMatrix(1, 1, 1, 1).correct == 2
    assert ConfusionMatrix(1, 1, 1, 1).incorrect == 2
    assert ConfusionMatrix.empty() == ConfusionMatrix(TP=0, FP=0, TN=0, FN=0)

    conf = ConfusionMatrix.empty()
    conf.push(True, True)
    conf.push(True, False)
    conf.push(False, True)
    conf.push(False, False)
    assert conf == ConfusionMatrix(TP=1, FP=1, TN=1, FN=1)

    assert ConfusionMatrix.empty().recall == 0
    assert ConfusionMatrix.empty().precision == 1
    assert ConfusionMatrix.empty().f1_score == 0
    assert ConfusionMatrix(0, 1, 0, 1).f1_score == 0
    assert round(ConfusionMatrix(40, 40, 40, 40).bootstrap_f1_score_standard_error(), 2) == 0.05
    assert round(ConfusionMatrix(40, 40, 40, 40).bootstrap_accuracy_standard_error(), 2) == 0.04
    assert round(ConfusionMatrix(40, 40, 40, 40).bootstrap_precision_standard_error(), 2) == 0.05
    assert round(ConfusionMatrix(40, 40, 40, 40).bootstrap_recall_standard_error(), 2) == 0.05

    with pytest.raises(ZeroDivisionError):
        _ = ConfusionMatrix.empty().accuracy

    assert ConfusionMatrix(1, 1, 0, 0) + ConfusionMatrix(0, 0, 1, 1) == ConfusionMatrix(1, 1, 1, 1)
    conf = ConfusionMatrix(1, 1, 0, 0)
    conf += ConfusionMatrix(0, 0, 1, 1)
    assert conf == ConfusionMatrix(1, 1, 1, 1)


def test_confusion_matrix_by() -> None:
    conf_by = ConfusionMatrixBy.empty(("a", "b"))

    conf_by.push({"a": 1, "b": 1}, True, True)
    conf_by.push({"a": 1, "b": 1}, True, False)
    conf_by.push({"a": 1, "b": 2}, False, True)
    conf_by.push({"a": 2, "b": 2}, False, False)
    assert conf_by.all == ConfusionMatrix(1, 1, 1, 1)
    assert conf_by.group_by_key("b") == {1: ConfusionMatrix(1, 1, 0, 0), 2: ConfusionMatrix(0, 0, 1, 1)}
    assert conf_by.group_by_key("b", filter_key_values={"a": 1}) == {1: ConfusionMatrix(1, 1, 0, 0),
                                                                     2: ConfusionMatrix(0, 0, 0, 1)}

    with pytest.raises(ValueError):
        _ = conf_by.group_by_key("c")

    conf_by = ConfusionMatrixBy.empty(tuple())
    conf_by.push({}, True, True)
    conf_by.push({}, False, False)
    assert conf_by.all == ConfusionMatrix(1, 0, 1, 0)
