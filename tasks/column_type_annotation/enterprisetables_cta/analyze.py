import json
import logging
import statistics

import hydra
from omegaconf import DictConfig

from llms4de.data import get_download_dir
from llms4de.data import load_json

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../../config/column_type_annotation", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name)
    stats = load_json(download_dir / "stats.json")

    def extract_rows(x: str) -> int:
        return json.loads(x)["COUNT(*)"]["0"]

    stats["num_rows"] = [extract_rows(x) for x in stats["num_rows"]]
    characteristics = {
        "number of tables": len(stats["num_cols"]),
        "tables per database": None,
        "mean columns per table": sum(stats["num_cols"]) / len(stats["num_cols"]),
        "median columns per table": statistics.median(stats["num_cols"]),
        "95th columns per table": statistics.quantiles(stats["num_cols"], n=20)[-1],
        "mean rows per table": sum(stats["num_rows"]) / len(stats["num_rows"]),
        "median rows per table": statistics.median(stats["num_rows"]),
        "95th rows per table": statistics.quantiles(stats["num_rows"], n=20)[-1],
        "sparsity": sum(stats["sparsity"]) / len(stats["sparsity"]),
        "non-numerical columns": stats["num_non_numerical_cols"] / (
                stats["num_non_numerical_cols"] + stats["num_numerical_cols"]),
        "numerical columns": stats["num_numerical_cols"] / (
                stats["num_non_numerical_cols"] + stats["num_numerical_cols"])
    }

    with open(download_dir / "characteristics.json", "w", encoding="utf-8") as file:
        json.dump(characteristics, file)
    logger.info("Done!")


if __name__ == "__main__":
    main()
