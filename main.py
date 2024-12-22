import os
import time
import json
import dotenv
import logging
import docker.models.containers
import docker
import requests
import message
import v2ray2json
import metrics

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

dotenv.load_dotenv(dotenv_path="./.env")
CONFIG_URL: str = os.getenv("CONFIG_URL")
TEST_URL: str = os.getenv("TEST_URL")
NETWORK: str = os.getenv("NETWORK")
LOOP_DELAY_SECONDS: int = int(os.getenv("LOOP_DELAY_SECONDS"))

metrics.setup()
docker_client = docker.from_env()


def is_subscription(config: str) -> bool:
    return config.split("://")[0] in ["http", "https"]


def main_loop() -> None:
    # Init configs url
    configs: list[str]

    if is_subscription(config=CONFIG_URL):
        configs = requests.get(CONFIG_URL).text.splitlines()
    else:
        configs = [CONFIG_URL]
    logging.info("Load configs successfully.")

    # Init docker image
    logging.info("Build docker image...")
    image, _ = docker_client.images.build(path=".", tag="gfw-xray-core")
    container: docker.models.containers.Container = None
    # TODO: handle async for each config
    for config in configs:
        logging.info(f"Generate config for:{config}")
        config_dict = v2ray2json.generateConfig(config=config)

        with open("./configs/config.json", "w") as file:
            json.dump(config_dict, file, sort_keys=True, indent=2)

        try:
            logging.info("Run xray core with the config....")
            container = docker_client.containers.run(
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

            # Ensure xray is running.
            time.sleep(1)

            # Check connection.
            logging.info("Try to request...")
            requests.get(
                timeout=10,
                url=TEST_URL,
                proxies={
                    "http": "socks5h://localhost:10808",
                    "https": "socks5h://localhost:10808",
                },
            ).text

            metrics.CONFIG_STATUS_GAUGE.labels(
                network=NETWORK, config_name=config_dict["_comment"]["remark"]
            ).set(1)
        except requests.exceptions.Timeout:
            metrics.CONFIG_STATUS_GAUGE.labels(
                network=NETWORK, config_name=config_dict["_comment"]["remark"]
            ).set(0)
            message.send_email_smtp(
                subject=f"Config not work in {NETWORK}",
                body=f"config={config}",
            )
            message.send_telegram_message(
                message=f"Config not work in {NETWORK}.\n{config}"
            )
            logging.warning(f"Not work config in {NETWORK}: {config}")
        except Exception:
            pass
        finally:
            if container is not None:
                container.stop()
                container.remove()


def main() -> None:
    while True:
        main_loop()
        time.sleep(LOOP_DELAY_SECONDS)


if __name__ == "__main__":
    main()
