"""CLI entry points for envault vault storage commands."""

import os
import sys
import getpass
import argparse
from pathlib import Path

from envault.storage import (
    set_secret,
    get_secret,
    delete_secret,
    list_keys,
    load_vault,
)


def _get_password(prompt: str = "Vault password: ") -> str:
    pw = os.environ.get("ENVAULT_PASSWORD")
    if pw:
        return pw
    return getpass.getpass(prompt)


def cmd_set(args: argparse.Namespace) -> None:
    password = _get_password()
    set_secret(args.key, args.value, password)
    print(f"✓ Set '{args.key}'")


def cmd_get(args: argparse.Namespace) -> None:
    password = _get_password()
    value = get_secret(args.key, password)
    if value is None:
        print(f"Key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)
    print(value)


def cmd_delete(args: argparse.Namespace) -> None:
    password = _get_password()
    removed = delete_secret(args.key, password)
    if removed:
        print(f"✓ Deleted '{args.key}'")
    else:
        print(f"Key '{args.key}' not found.", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    password = _get_password()
    keys = list_keys(password)
    if not keys:
        print("(vault is empty)")
    else:
        for k in keys:
            print(k)


def cmd_export(args: argparse.Namespace) -> None:
    """Print all secrets as KEY=VALUE lines suitable for shell export."""
    password = _get_password()
    data = load_vault(password)
    for k, v in sorted(data.items()):
        print(f"{k}={v}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Securely manage .env secrets in an encrypted local vault.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Store a secret")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_get = sub.add_parser("get", help="Retrieve a secret")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_del = sub.add_parser("delete", help="Remove a secret")
    p_del.add_argument("key")
    p_del.set_defaults(func=cmd_delete)

    p_list = sub.add_parser("list", help="List all secret keys")
    p_list.set_defaults(func=cmd_list)

    p_export = sub.add_parser("export", help="Export all secrets as KEY=VALUE")
    p_export.set_defaults(func=cmd_export)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
