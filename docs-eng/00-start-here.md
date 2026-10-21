# Module 00, Start Here

[Português](../docs/00-comece-aqui.md) · English

`WEEK 06 // Central RESTful API, Part 2: Integration`

---

## // Welcome to Week 06

Imagine you have two finished pieces. The first is a **web page** for the Study Group Finder (*Buscador de Grupos de Estudo*), with a list, a form and buttons. The second is an **API**, a Python program that stores the study groups and the subjects and answers requests over the network. Each piece works on its own. The trouble starts when you try to connect them: the page asks for the list of groups, the API responds, and the list **does not show up**. No error on the server, no wrong line of code, and still the page does not receive the data.

This week is about that connection. It is called **integration**, and almost everything that goes wrong in it comes down to something you have not seen yet: **the browser has its own rules about which pages may read the responses of which servers**.

> **THIS WEEK IS STANDALONE**
> This is Part 2 of the "Central RESTful API" topic, but it was written to be read **on its own**. You do not need to have built an API before: this week's API comes **ready**, and you only run it. You do not need to know JavaScript either: Modules 04 to 07 introduce what integration requires.

## // What full-stack integration is

> **FULL-STACK: IN SIMPLE WORDS**
> A *full-stack* application has both ends: the **front-end** (what runs in the browser and shows up on screen) and the **back-end** (what runs on a server and holds the data and the rules). **Integration** is the set of decisions that makes the two ends talk to each other: which addresses to call, in what format to exchange the data, and what to do when something fails.

<div align="center">
<img src="../docs/assets/svg/arquitetura-fullstack.svg" alt="The page in the browser calling the API with fetch, each one on a different port" width="640">
</div>

Notice one detail in the drawing: both ends run on **your computer**, but on **different ports** (5500 and 8000). To the browser, that makes them two distinct "sites", and that is why CORS comes into play. Module 08 explains the concept of an origin, and Module 09 solves the problem.

## // What you will build by the end of the week

- A **web page** in plain HTML, CSS and JavaScript (no frameworks) that lists, searches, creates, edits and deletes study groups, talking to the API.
- An **API** in FastAPI configured to safely accept the calls coming from that page (CORS).
- The handling of the **screen states**: loading, empty list, validation error, conflict and API down.
- The habit of **diagnosing** through the browser's Network tab, the main tool of anyone who integrates systems.

## // What is still left out

> **NOT THIS WEEK YET**
> The data lives **in memory**: it goes back to its initial state every time the API restarts. Also left out are login, cookies and tokens, the database, publishing both ends to the internet, and front-end frameworks (React, Vue and others). Here, the goal is to understand integration itself, with nothing hiding what happens.

## // What you need to get started

- A computer running Windows, macOS or Linux, and permission to install programs.
- **Python 3.10 or newer**, to run the ready-made API (Module 03 shows how).
- A current browser, such as Chrome, Edge or Firefox.
- A text or code editor (any one will do) and a terminal.
- An internet connection, to install the API's library.
- **No prior knowledge** of APIs, JavaScript or CORS.

> **VERSIONS AND DATE CONSULTED**
> The material was verified with **FastAPI 0.143.0**, Starlette 1.7.0, Pydantic 2.13.5, Uvicorn 0.54.0 and Python 3.12.3. The official FastAPI documentation and the MDN documentation (on CORS) were consulted on **2026-10-08**. The server responses quoted in the modules come from **real runs**, made with `curl`. The **browser** behaviours (the CORS block, the Network tab) follow the MDN documentation and were **not reproduced in a browser** while the material was produced: the error messages shown appear as "typical text", and they vary between browsers. FastAPI is a `0.x` library and changes often: if anything differs from what is here, the official documentation is the reference.

## // The two tracks

**If you are starting out**, you have never connected a page to an API. The main path assumes that: Modules 01 to 14 introduce each concept before it is needed, and end with a working application.

**If you already have experience**, you have made API calls before. Modules 15 and 16, clearly marked as the veteran track and placed after the essentials, cover **request middlewares** and **JSON standardization**. Module 17 is a bonus on the same track: how to test the integration.

Both tracks build the same application. What changes between them is the depth.

## // Map of Week 06

| Module | Content | You will be able to |
|---|---|---|
| 01 | HTTP from the browser | Read a request and a response in the Network tab |
| 02 | Headers | Understand the headers that show up in almost every integration error |
| 03 | The API we will use | Run the API and test it with Swagger and `curl` |
| 04 | Essential JavaScript for integration | Write functions, objects and arrays in JavaScript |
| 05 | The DOM: reading and changing the page | Show data on screen, safely |
| 06 | Async: Promises and `async/await` | Wait for a response without freezing the page |
| 07 | `fetch`: the first request | Call the API and tell a network error from an HTTP error |
| 08 | Serving the front-end and the origin | Understand why two ports are two origins |
| 09 | CORS: the browser blocks | Configure CORS and diagnose it when it fails |
| 10 | Listing groups on the page | Build the list, with search and filter |
| 11 | Sending data: form and `POST` | Create groups and show the errors field by field |
| 12 | Editing and deleting: `PATCH` and `DELETE` | Change and remove, handling the response with no body |
| 13 | Pagination and exposed headers | Paginate with the total coming from a header |
| 14 | Guided project | Have the complete full-stack application |
| 15 | Request middlewares (veteran) | Identify, measure and log every request |
| 16 | JSON standardization (veteran) | Use a single response and error format |
| 17 | Testing the integration (veteran, bonus) | Automate the verification of both ends |

Each module is a standalone file, but they were written to be read in this order: CORS only makes sense after you understand origins, and the screen only makes sense after CORS is solved.

---

**Next module:** `01-http-from-the-browser.md`, before writing code, learn to see what the browser and the API exchange with each other.

`Study Material // Coffee & Code`
