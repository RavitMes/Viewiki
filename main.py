import argparse
import logging.config
import logging
from config import LOG_CONF, HOST, DEBUG
from app import create_app


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", action="store", default="5001")
    args = parser.parse_args()
    return args


def main():
    logging.config.fileConfig(LOG_CONF)
    args = parse_args()
    port = int(args.port)
    app = create_app()
    app.run(host=HOST, port=port, debug=DEBUG)


if __name__ == "__main__":
    main()

