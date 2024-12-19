import os
import time
import json
import dotenv
import logging
import docker.models.containers
import requests
import docker
import v2ray2json

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

dotenv.load_dotenv(dotenv_path="./.env")
docker_client = docker.from_env()


def is_subscription(config: str) -> bool:
    return config.split("://")[0] in ["http", "https"]


def main() -> None:
    # Init configs url
    config_url: str = os.getenv("CONFIG_URL")
    configs: list[str]

    if is_subscription(config=config_url):
        configs = requests.get(config_url).text.splitlines()
    else:
        configs = [config_url]
    logging.info("Load configs successfully.")

    # Init docker image
    logging.info("Build docker image...")
    image, _ = docker_client.images.build(path=".", tag="gfw-xray-core")
    for config in configs:
        logging.info(f"Generate config for:{config}")
        config_dict = v2ray2json.generateConfig(config=config)

        with open("./configs/config.json", "w") as file:
            json.dump(config_dict, file, sort_keys=True, indent=2)

        logging.info("Run xray core with the config....")
        container: docker.models.containers.Container = (
            docker_client.containers.run(
                image=image,
                detach=True,
                volumes={
                    os.path.abspath("./configs"): {
                        "mode": "rw",
                        "bind": "/app/configs/",
                    }
                },
                ports={"10808": "10808"},
            )
        )

        # Ensure xray is running.
        time.sleep(1)

        # Check connection.
        logging.info("Try to request...")
        logging.info(
            requests.get(
                url="https://ifconfig.me",
                proxy={
                    "http": "socks5h://localhost:10808",
                    "https": "socks5h://localhost:10808",
                },
            ).text
        )

        container.stop()
        container.remove()


if __name__ == "__main__":
    main()
