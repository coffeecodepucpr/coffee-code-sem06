# Deliveries | Week 06

[Português](README.md) · English

This is where the deliveries of everyone who did Week 06 live. The list with each person's project is in the [main README](../README.en.md#the-classs-deliveries).

## How to deliver

1. **Fork** this repository (the *Fork* button, at the top right).
2. In your fork, create the folder `entregas/Nome Sobrenome/`, with your first and last name.
3. Put your files inside it, following the structure below.
4. Commit and push to your fork.
5. Open a **Pull Request** to this repository and fill in the template that shows up.

After the merge, your delivery goes into the main README's table.

> **Prefer to keep the project in your own repository?** That works too. Send the link on Discord or [open an issue](../../../issues/new) here with the link to the week's folder, and it goes into the table just the same. Just take care with the `README.md`, as explained below, because it is the first thing people will see.

## Expected structure

This week the delivery has **two ends**, the API and the page:

```text
entregas/Nome Sobrenome/
└── projeto-fullstack/
    ├── api/
    │   ├── main.py
    │   ├── dados.py
    │   ├── schemas.py
    │   └── requirements.txt
    ├── frontend/
    │   ├── index.html
    │   ├── estilos.css
    │   ├── api.js
    │   ├── ui.js
    │   └── app.js
    └── README.md
```

- Do not send the `.venv` folder, `__pycache__` files or a `.env` file. A `.gitignore` with those three lines takes care of it.
- Do not send the `node_modules` folder, if you did the page tests from Module 17.
- File names in lower case, separated by hyphens or underscores and **with an extension**.
- Only change files inside your own folder.

## What your README needs to have

Your folder's `README.md` is your project's cover. Whoever opens it has to understand, without you explaining:

- **the project's name** as the title;
- **one sentence** saying what the application does;
- **how to run both ends**, in two terminals: the API (`pip install -r requirements.txt` and `fastapi dev main.py`) and the page (`python3 -m http.server 5500 --bind 127.0.0.1`);
- **the two origins** involved, and which ones are allowed in CORS;
- **the routes** the page uses;
- **the verification script** from Module 14, with the result of each step you went through.

## Already delivered in another week?

No problem repeating the same project. Just remember that each week is a complete folder: send the updated version here too.
