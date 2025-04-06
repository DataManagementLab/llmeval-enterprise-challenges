import collections
import logging
import random
import statistics
from typing import Callable, Any

import attrs

logger = logging.getLogger(__name__)

bootstrap_random = random.Random(981100968)


def bootstrap_standard_error(
        population: dict[str, int],
        score_function: Callable[[dict[str, int]], float],
        num_rounds: int
) -> float:
    """Determine the standard error of a score with bootstrapping.

    Args:
        population: The population to sample from.
        score_function: The function which transforms counts into a score.
        num_rounds: The number of rounds for bootstrapping

    Returns:
        The standard error of the score.
    """
    total = sum(population.values())
    if total == 0:
        raise AssertionError("cannot bootstrap standard error from empty population")
    entries = list(population.keys())
    weights = [count / total for count in population.values()]
    scores = []
    for _ in range(num_rounds):
        counts = dict(collections.Counter(bootstrap_random.choices(entries, weights, k=total)))
        for entry in entries:
            if entry not in counts.keys():
                counts[entry] = 0
        scores.append(score_function(counts))

    return statistics.stdev(scores)


@attrs.define
class Accuracy:
    """Accuracy metric."""
    correct: int
    incorrect: int

    @property
    def total(self) -> int:
        """Total number of instances."""
        return self.correct + self.incorrect

    @property
    def accuracy(self) -> float:
        """Accuracy score."""
        return self.correct / self.total

    @classmethod
    def empty(cls) -> "Accuracy":
        """Create an empty accuracy object."""
        return cls(0, 0)

    def push(self, is_correct: bool) -> None:
        """Include the given instance in the accuracy.

        Args:
            is_correct: Whether the instance is correct.
        """
        if is_correct:
            self.correct += 1
        else:
            self.incorrect += 1

    def __add__(self, other: "Accuracy") -> "Accuracy":
        return Accuracy(self.correct + other.correct, self.incorrect + other.incorrect)

    def bootstrap_accuracy_standard_error(self, *, num_rounds: int = 1_000) -> float:
        """Determine the accuracy's standard error with bootstrapping.

        Args:
            num_rounds: The number of rounds for bootstrapping.

        Returns:
            The accuracy's standard error.
        """
        return bootstrap_standard_error(
            {"correct": self.correct, "incorrect": self.incorrect},
            lambda counts: Accuracy(**counts).accuracy,
            num_rounds
        )


@attrs.define
class AccuracyBy:
    """Accuracy by key."""
    keys: tuple[str, ...]
    mapping: dict[tuple[Any, ...], Accuracy]

    @classmethod
    def empty(cls, keys: tuple[str, ...]) -> "AccuracyBy":
        """Create an empty accuracy by object."""
        return cls(keys, collections.defaultdict(Accuracy.empty))

    def _key_values_dict_to_tuple(self, key_values: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(key_values[key] for key in self.keys)

    def push(self, key_values: dict[str, Any], is_correct: bool) -> None:
        """Include the given instance in the accuracy for the given key values.

        Args:
            key_values: The key values for the instance.
            is_correct: Whether the instance is correct.
        """
        self.mapping[self._key_values_dict_to_tuple(key_values)].push(is_correct)

    @property
    def all(self) -> Accuracy:
        """Return the accuracy across all key values."""
        res = Accuracy.empty()
        for accuracy in self.mapping.values():
            res += accuracy
        return res

    def group_by_key(self, key: str, *, filter_key_values: dict[str, Any] | None = None) -> dict[Any, Accuracy]:
        """Group the accuracy by the given key.

        Args:
            key: The key to group by.
            filter_key_values: An optional dictionary of values to filter by.

        Returns:
            Mapping from key value to accuracy.
        """
        res = collections.defaultdict(Accuracy.empty)

        for key_values, accuracy in self.mapping.items():
            if filter_key_values is not None:
                skip = False
                for k, v in filter_key_values.items():
                    if key_values[self.keys.index(k)] != v:
                        skip = True
                        break
                if skip:
                    continue

            value = key_values[self.keys.index(key)]
            res[value] += accuracy

        return res


@attrs.define
class ConfusionMatrix:
    """ConfusionMatrix matrix with precision, recall, and F1 score."""
    TP: int
    FP: int
    TN: int
    FN: int

    @property
    def total(self) -> int:
        """Total number of instances."""
        return self.TN + self.FP + self.FN + self.TP

    @property
    def precision(self) -> float:
        """Precision score."""
        if self.TP + self.FP == 0:
            return 1
        return self.TP / (self.TP + self.FP)

    @property
    def recall(self) -> float:
        """Recall score."""
        if self.TP + self.FN == 0:
            return 0
        return self.TP / (self.TP + self.FN)

    @property
    def f1_score(self) -> float:
        """F1 score."""
        if self.precision + self.recall == 0:
            return 0
        return 2 * self.precision * self.recall / (self.precision + self.recall)

    @property
    def correct(self) -> int:
        """Number of correct instances."""
        return self.TP + self.TN

    @property
    def incorrect(self) -> int:
        """Number of incorrect instances."""
        return self.FP + self.FN

    @property
    def accuracy(self) -> float:
        """Accuracy score."""
        return self.correct / self.total

    @classmethod
    def empty(cls) -> "ConfusionMatrix":
        """Create an empty confusion matrix object."""
        return cls(0, 0, 0, 0)

    def push(self, prediction: bool, ground_truth: bool) -> None:
        """Include the given instance in the confusion matrix.

        Args:
            prediction: The predicted value.
            ground_truth: The ground truth value.
        """
        self.TP += int(prediction and ground_truth)
        self.FP += int(prediction and not ground_truth)
        self.TN += int(not prediction and not ground_truth)
        self.FN += int(not prediction and ground_truth)

    def __add__(self, other: "ConfusionMatrix") -> "ConfusionMatrix":
        return ConfusionMatrix(
            self.TP + other.TP,
            self.FP + other.FP,
            self.TN + other.TN,
            self.FN + other.FN
        )

    def bootstrap_f1_score_standard_error(self, *, num_rounds: int = 1_000) -> float:
        """Determine the F1 score's standard error with bootstrapping.

        Args:
            num_rounds: The number of rounds for bootstrapping.

        Returns:
            The F1 score's standard error.
        """
        return bootstrap_standard_error(
            {"TP": self.TP, "FP": self.FP, "TN": self.TN, "FN": self.FN},
            lambda counts: ConfusionMatrix(**counts).f1_score,
            num_rounds
        )

    def bootstrap_accuracy_standard_error(self, *, num_rounds: int = 1_000) -> float:
        """Determine the accuracy's standard error with bootstrapping.

        Args:
            num_rounds: The number of rounds for bootstrapping.

        Returns:
            The accuracy's standard error.
        """
        return bootstrap_standard_error(
            {"TP": self.TP, "FP": self.FP, "TN": self.TN, "FN": self.FN},
            lambda counts: ConfusionMatrix(**counts).accuracy,
            num_rounds
        )

    def bootstrap_recall_standard_error(self, *, num_rounds: int = 1_000) -> float:
        """Determine the recall's standard error with bootstrapping.

        Args:
            num_rounds: The number of rounds for bootstrapping.

        Returns:
            The recall's standard error.
        """
        return bootstrap_standard_error(
            {"TP": self.TP, "FP": self.FP, "TN": self.TN, "FN": self.FN},
            lambda counts: ConfusionMatrix(**counts).recall,
            num_rounds
        )

    def bootstrap_precision_standard_error(self, *, num_rounds: int = 1_000) -> float:
        """Determine the precision's standard error with bootstrapping.

        Args:
            num_rounds: The number of rounds for bootstrapping.

        Returns:
            The recall's standard error.
        """
        return bootstrap_standard_error(
            {"TP": self.TP, "FP": self.FP, "TN": self.TN, "FN": self.FN},
            lambda counts: ConfusionMatrix(**counts).precision,
            num_rounds
        )


@attrs.define
class ConfusionMatrixBy:
    """ConfusionMatrix by key."""
    keys: tuple[str, ...]
    mapping: dict[tuple[Any, ...], ConfusionMatrix]

    @classmethod
    def empty(cls, keys: tuple[str, ...]) -> "ConfusionMatrixBy":
        """Create an empty ConfusionMatrixBy object."""
        return cls(keys, collections.defaultdict(ConfusionMatrix.empty))

    def _key_values_dict_to_tuple(self, key_values: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(key_values[key] for key in self.keys)

    def push(self, key_values: dict[str, Any], prediction: bool, ground_truth: bool) -> None:
        """Include the given instance in the confusion for the given key values.

        Args:
            key_values: The key values for the instance.
            prediction: The predicted value.
            ground_truth: The ground truth value.
        """
        self.mapping[self._key_values_dict_to_tuple(key_values)].push(prediction, ground_truth)

    @property
    def all(self) -> ConfusionMatrix:
        """Return the confusion matrix across all key values."""
        res = ConfusionMatrix.empty()
        for confusion in self.mapping.values():
            res += confusion
        return res

    def group_by_key(self, key: str, *, filter_key_values: dict[str, Any] | None = None) -> dict[str, ConfusionMatrix]:
        """Group the confusion matrix by the given key.

        Args:
            key: The key to group by.
            filter_key_values: An optional dictionary of values to filter by.

        Returns:
            Mapping from key value to confusion matrix.
        """
        res = collections.defaultdict(ConfusionMatrix.empty)

        for key_values, confusion in self.mapping.items():
            if filter_key_values is not None:
                skip = False
                for k, v in filter_key_values.items():
                    if key_values[self.keys.index(k)] != v:
                        skip = True
                        break
                if skip:
                    continue

            value = key_values[self.keys.index(key)]
            res[value] += confusion

        return res
