import logging

import attrs
import hydra
import pandas as pd
import tiktoken
from hydra.core.config_store import ConfigStore

from llms4de.data import get_experiments_path, dump_str

logger = logging.getLogger(__name__)


@attrs.define
class Config:
    model: str = "gpt-4o-2024-08-06"


ConfigStore.instance().store(name="config", node=Config)


@hydra.main(version_base=None, config_name="config")
def main(cfg: Config) -> None:
    encoding = tiktoken.encoding_for_model(cfg.model)

    experiment_dir = get_experiments_path() / "enterprise_knowledge_text2signal"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    documentation_dir = experiment_dir

    entries = pd.read_csv(documentation_dir / "entries.csv")
    entries["html_content_without_multiple_examples"] = entries["html_content"].apply(html_remove_multiple_examples)
    entries["str_content_without_multiple_examples"] = entries["str_content"].apply(str_remove_multiple_examples)

    s = [build_str(row["breadcrumbs"], row["html_content"]) for _, row in entries.iterrows()]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"html_full_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["html_content"])
         for _, row in entries.iterrows() if no_detailed_functions(row["breadcrumbs"])]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"html_no_detailed_functions_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["html_content_without_multiple_examples"])
         for _, row in entries.iterrows()]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"html_without_multiple_examples_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["html_content_without_multiple_examples"])
         for _, row in entries.iterrows() if no_detailed_functions(row["breadcrumbs"])]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"html_no_detailed_functions_without_multiple_examples_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["str_content"]) for _, row in entries.iterrows()]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"str_full_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["str_content"])
         for _, row in entries.iterrows() if no_detailed_functions(row["breadcrumbs"])]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"str_no_detailed_functions_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["str_content_without_multiple_examples"])
         for _, row in entries.iterrows()]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"str_without_multiple_examples_{k_tokens}K.txt")

    s = [build_str(row["breadcrumbs"], row["str_content_without_multiple_examples"])
         for _, row in entries.iterrows() if no_detailed_functions(row["breadcrumbs"])]
    s = "\n".join(s)
    k_tokens = len(encoding.encode(s)) // 1000 + 1
    dump_str(s, documentation_dir / f"str_no_detailed_functions_without_multiple_examples_{k_tokens}K.txt")

    logger.info("Done!")


def html_remove_multiple_examples(content: str) -> str:
    if "<h2>Example 2</h2>" in content:
        content = content[:content.index("<h2>Example 2</h2>")]
    return content


def str_remove_multiple_examples(content: str) -> str:
    if "Example 2" in content:
        content = content[:content.index("Example 2")]
    return content


def no_detailed_functions(breadcrumbs: str) -> bool:
    if breadcrumbs.count("Functions") >= 2:
        idx = breadcrumbs.index("Functions", breadcrumbs.index("Functions") + 1) + 10
        s = breadcrumbs[idx:idx + 2]
        if s != "" and s == s.upper():
            return True
    return False


def build_str(breadcrumbs: str, content: str) -> str:
    return f"{breadcrumbs} {content}"


if __name__ == "__main__":
    main()
