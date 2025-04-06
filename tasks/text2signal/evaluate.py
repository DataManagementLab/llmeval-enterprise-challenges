import collections
import logging
import os
import sys
from pathlib import Path

import hydra
import requests
import tqdm
from dotenv import load_dotenv
from exceptiongroup import catch
from omegaconf import DictConfig

from llms4de.data import get_instances_dir, get_results_dir, load_json, load_str, dump_json, \
    get_predictions_dir, dump_cfg

logger = logging.getLogger(__name__)


class SignavioAuthenticator:
    def __init__(self, system_instance, tenant_id, email, pw):
        self.system_instance = system_instance
        self.tenant_id = tenant_id
        self.email = email
        self.pw = pw

    """
    Takes care of authentication against Signavio systems
    """

    def authenticate(self):
        """
        Authenticates user at Signavio system instance and initiates session.
        Returns:
            dictionary: Session information
        """
        login_url = self.system_instance + "/p/login"
        data = {"name": self.email, "password": self.pw, "tokenonly": "true"}
        # if "tenant_id" in locals():
        #    data["tenant"] = self.tenant_id
        data["tenant"] = self.tenant_id
        # authenticate
        login_request = requests.post(login_url, data)

        # retrieve token and session ID
        auth_token = login_request.content.decode("utf-8")
        jsesssion_ID = login_request.cookies["JSESSIONID"]

        # The cookie is named 'LBROUTEID' for base_url 'editor.signavio.com'
        # and 'editor.signavio.com', and 'AWSELB' for base_url
        # 'app-au.signavio.com' and 'app-us.signavio.com'
        lb_route_ID = login_request.cookies["LBROUTEID"]

        # return credentials
        return {
            "jsesssion_ID": jsesssion_ID,
            "lb_route_ID": lb_route_ID,
            "auth_token": auth_token,
        }


def signal_template(signal, view):
    return f'SELECT {signal} FROM "{view}"'


def credentials_actualization(system_instance, workspace_id, user_name, pw, auth={}, workspace_name=""):
    # get credentials for current session. They are valid for 24 hours
    authenticator = SignavioAuthenticator(system_instance, workspace_id, user_name, pw)
    auth_data = authenticator.authenticate()
    cookies = {'JSESSIONID': auth_data['jsesssion_ID'], 'LBROUTEID': auth_data['lb_route_ID']}
    headers = {'Accept': 'application/json', 'x-signavio-id': auth_data['auth_token']}
    print(auth_data['jsesssion_ID'], auth_data['lb_route_ID'])
    print(auth_data['auth_token'])
    auth[workspace_name] = {"cookies": cookies, "headers": headers}
    return auth


@hydra.main(version_base=None, config_path="../../config/text2signal", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    instances_dir = get_instances_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    predictions_dir = get_predictions_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name)
    results_dir = get_results_dir(cfg.task_name, cfg.dataset.dataset_name, cfg.exp_name, clear=True)

    errors = collections.Counter()
    results = {}
    ix = 0
    instance_dirs = sorted(instances_dir.glob("*/"))

    for instance_dir in tqdm.tqdm(instance_dirs,
                                  desc=f"{cfg.task_name} - {cfg.dataset.dataset_name} - {cfg.exp_name} - evaluate"):
        prediction_dir = predictions_dir / instance_dir.name
        ground_truth = load_json(instance_dir / "signal.json")
        prediction = load_str(prediction_dir / "prediction.txt")
        error = load_json(prediction_dir / "error.json")
        if prediction != "api_request_failed":

            sys.path.append("./")
            env_path = Path('.env')

            load_dotenv(dotenv_path=env_path)

            auth = {}
            user_name = os.environ.get('MY_SIGNAVIO_NAME', None)  # username
            pw = os.environ.get('MY_SIGNAVIO_PASSWORD', None)  # Signavio password

            signal_endpoint = cfg.dataset.system_instance + cfg.dataset.signal_endpoint

            auth = credentials_actualization(cfg.dataset.system_instance, cfg.dataset.workspace_id, user_name, pw,
                                             auth=auth,
                                             workspace_name=cfg.dataset.workspace_name)
            q = {'query': prediction}
            query_request = requests.post(
                signal_endpoint,
                cookies=auth[cfg.dataset.workspace_name]["cookies"],
                headers=auth[cfg.dataset.workspace_name]["headers"],
                json=q)
            prediction_result_validation = query_request.json()
            dump_json(prediction_result_validation, instance_dir / "prediction_validation.json")

            q = {'query': ground_truth["new_query"]}
            query_request = requests.post(
                signal_endpoint,
                cookies=auth[cfg.dataset.workspace_name]["cookies"],
                headers=auth[cfg.dataset.workspace_name]["headers"],
                json=q)
            groundtruth_result_validation = query_request.json()
            dump_json(groundtruth_result_validation, instance_dir / "groundtruth_validation.json")

            status = "valid query wrong result"

            try:
                status = prediction_result_validation["errorType"]
            except Exception as e:
                if groundtruth_result_validation == prediction_result_validation:
                    status = "valid query correct result"

            results[ix] = {"status": status}
            ix += 1

    if errors.total() > 0:
        logger.warning(f"errors: {errors}")
    dump_json(results, results_dir / "results.json")

    dump_cfg(cfg, results_dir / "config.cfg")


if __name__ == "__main__":
    main()
