# Install

Create a virtual env

```bash
 python -m venv env
 ```

Activate virtual env
```bash
source env/bin/activate
```

Install packages from `requirements.txt`
```bash
pip install -r requirements.txt
```


Create the following files
1. Copy `.env.dist` to `.env` and complete
2. Copy `users.json.dist` to `users.json` and add users
3. Copy `email_template.txt.dist` to `email_template.txt` and update if needed


# Usage

To display debug messages set `MODE` to `dev` in `.env`

```bash
MODE=dev
```

To send emails set `SEND_EMAIL` to `true` in `.env`

```bash
SEND_EMAIL=true
```


To run the script without seeing the output stream the command output to a file in `debug`

```bash
python app.py > debug/output.txt
```
No peaking at the output file!