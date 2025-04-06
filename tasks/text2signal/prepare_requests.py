import logging
import random

import hydra
import tqdm
from omegaconf import DictConfig, OmegaConf

from llms4de.data import get_instances_dir, get_requests_dir, load_json, dump_json, dump_cfg
from llms4de.model.generic import max_tokens_for_ground_truth
from llms4de.prompting.template import fill_chat_template

logger = logging.getLogger(__name__)

_prepare_requests_random = random.Random(859962185)


def read_file(filename):
    """
    Reads the content of a text file and returns it as a string.

    :param filename: The path to the text file.
    :return: The content of the file as a string.
    """
    file = "./experiments/enterprise_knowledge_text2signal/" + filename
    with open(file, 'r') as file:
        content = file.read()
    return content


@hydra.main(version_base=None, config_path="../../config/text2signal", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    requests_dir = get_requests_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    # all_column_names = load_json(instances_dir / "table_header.json")

    instance_paths = list(sorted(instances_dir.glob("*/")))
    for path in tqdm.tqdm(instance_paths,
                          f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - prepare requests"):
        # load instance
        signal = load_json(path / "signal.json")

        ground_truth = str(signal)

        request = {
            "model": cfg.model,
            "max_tokens": max_tokens_for_ground_truth(
                ground_truth,
                cfg.api_name,
                cfg.model,
                cfg.max_tokens_over_ground_truth
            ),
            "temperature": cfg.temperature
        }
        new_signal = signal['description_llm']
        old_view = signal['view']
        new_view = signal['new_view']
        new_signal = new_signal.replace(old_view, new_view)

        if (cfg.mode == "one_shot"):
            request["messages"] = fill_chat_template(
                OmegaConf.to_container(cfg.prompt_chat_oneshot_template),
                signal=new_signal,
                newline="\n"
            )
        elif (cfg.mode == "zero_shot"):
            request["messages"] = fill_chat_template(
                OmegaConf.to_container(cfg.prompt_chat_template),
                signal=new_signal,
                newline="\n"
            )
        elif (cfg.mode == "RAG"):
            request["messages"] = fill_chat_template(
                OmegaConf.to_container(cfg.prompt_chat_RAG_template),
                signal=new_signal,
                documentation=read_file(cfg.rag_file),
                newline="\n"
            )
        elif (cfg.mode == "few_shot"):
            request["messages"] = fill_chat_template(
                OmegaConf.to_container(cfg.prompt_chat_fewshot_template),
                signal=new_signal,
                newline="\n"
            )
        elif (cfg.mode == "few_and_docu"):
            request["messages"] = fill_chat_template(
                OmegaConf.to_container(cfg.prompt_chat_fewshot_doc_template),
                signal=new_signal,
                documentation=read_file(cfg.rag_file),
                newline="\n"
            )

        else:
            logger.error("No mode identified")

        dump_json(request, requests_dir / f"{path.name}.json")

    dump_cfg(cfg, requests_dir / "config.cfg")


if __name__ == "__main__":
    main()
