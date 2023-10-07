import os
import sys
import requests
import time
import json
from argparse import ArgumentParser, Namespace
import shlex

# https://sabnzbd.org/wiki/configuration/4.1/scripts/notification-scripts

def main():
    args = parse_args()

    now = int(time.time() * 1000)
    tags = [f"sabnzbd_{args.notification_type}"]
    text = f"{args.notification_title}<br/>{args.notification_text}"
    
    post_annotation(args, tags, text, now)

    sys.exit(0)

def post_annotation(args: Namespace, tags: list, text: str, start_time: int) -> None:
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(args.grafana_token)
    }
    payload = {
        "tags": tags,
        "text": text,
        "time": start_time,
        "timeEnd": start_time,
        "dashboardUID": args.grafana_dashboard_uid
    }
    response = requests.post(
        f'{args.grafana_url}/api/annotations',
        data=json.dumps(payload),
        headers=headers
    )
    response.raise_for_status()

def parse_args() -> Namespace:
    parser = ArgumentParser(
        prog='SABnzbd Grafana Notify Script',
        description='Creates grafana annotations based on SABnzbd notifications',
        epilog='See github.com/jan-di/sabnzbd-notify-grafana',
    )

    # Predefined positional arguments by SABnzbd
    parser.add_argument('script_path')
    parser.add_argument('notification_type')
    parser.add_argument('notification_title')
    parser.add_argument('notification_text')

    # Additional arguments via parameters env var
    parser.add_argument('-u', dest='grafana_url', required=True)
    parser.add_argument('-t', dest='grafana_token', required=True)
    parser.add_argument('-d', dest='grafana_dashboard_uid', required=True)

    # Combine actual args with args from environment variable
    parameters = os.environ.get("SAB_NOTIFICATION_PARAMETERS", "")
    all_args = sys.argv + shlex.split(parameters)

    return parser.parse_args(all_args)

if __name__ == "__main__":
    main()