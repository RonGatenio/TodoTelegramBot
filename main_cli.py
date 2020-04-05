import argparse
import config
import todo_bot


def start_polling(args):
    todo_bot.run_polling(args.api_token)


def start_webhooks(args):
    todo_bot.run_webhooks(args.api_token, args.url, args.port)


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=start_polling)
    parser.add_argument('-t', '--token', 
        metavar='TELEGRAM_API_TOKEN', 
        default=config.TELEGRAM_API_TOKEN, 
        required=True,
    )

    subparsers  = parser.add_subparsers()
    webhooks_parser = subparsers.add_parser('webhooks', aliases=['wh'], help='use webhooks instead of polling')
    webhooks_parser.add_argument('url')
    webhooks_parser.add_argument('port', type=int)
    webhooks_parser.set_defaults(func=start_webhooks)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
