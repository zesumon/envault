# envault

> A CLI tool for securely managing and syncing .env files across development environments using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

Initialize a vault in your project directory:

```bash
envault init
```

Store your `.env` file securely:

```bash
envault store --env .env --name myproject
```

Sync and restore on another machine:

```bash
envault pull myproject --output .env
```

List all stored environments:

```bash
envault list
```

Encrypt and share with a teammate using a passphrase:

```bash
envault export myproject --passphrase "shared-secret"
```

---

## How It Works

envault encrypts your `.env` files using AES-256 encryption before storing them locally. Secrets never leave your machine unless you explicitly export them. Each vault is locked with a master key derived from your system credentials or a custom passphrase.

---

## Requirements

- Python 3.8+
- Works on Linux, macOS, and Windows

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.