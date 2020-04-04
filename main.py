import argparse
from todo_bot import run


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('api_token')

    args = parser.parse_args()
    run(args.api_token)


if __name__ == "__main__":
    main()
