<a id="readme-top"></a>



<!-- PROJECT SHIELDS -->
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<h3 align="center">Home Budget</h3>

  <p align="center">
    Personal home budget project
    <br />

</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

A self-hosted personal budget tracking application inspired by **YNAB**, built with **Python (Flask)** and **PostgreSQL**, containerized using **Docker**. This project is aimed at gaining hands-on experience with backend architecture, Docker, and budgeting logic for a professional Python portfolio.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

[![Python][Python]][Python-url]
[![Docker][Docker]][Docker-url]
[![HTML][HTML]][HTML-url]
[![CSS][CSS]][CSS-url]
[![JavaScript][JavaScript]][JavaScript-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📦 Project Structure

```
budget-project/
├── Python/                     # Main Python application source
│   ├── api/                    # API routes (Flask Blueprints)
│   ├── extensions/             # Extensions (DB, login manager, etc.)
│   ├── models/                 # SQLAlchemy models
│   ├── static/                 # Static assets (CSS, JS)
│   │   ├── css/                # Stylesheets
│   │   └── js/                 # JavaScript files
│   ├── templates/              # Jinja2 HTML templates
│   │   └── icons/              # SVG or icon partials
│   └── web/                    # Web page routes / views
├── Postgres/
│   ├── init.sql                # DB schema
│   ├── DB.erd.json             # DB ERD Diagram
│   └── init_data.sql           # Sample seed data
├── docker-compose.yml          # Docker orchestration
└── README.md                   # Project documentation
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## 🚀 Getting Started

### Prerequisites

- Docker + Docker Compose

This application requires a .env file to store configuration and sensitive credentials. Create a file named .env in the root directory with the following variables:
```sh
# PostgreSQL configuration
POSTGRES_USER=dkrysa
POSTGRES_PASSWORD=dawidkrysa
POSTGRES_DB=budget

# Security & Auth
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=ES256
PRIVATE_KEY="..."    # your ES256 private key
PUBLIC_KEY="..."     # your ES256 public key
INITIAL_ADMIN_EMAIL=dawidpkrysa@gmail.com
INITIAL_ADMIN_PASSWORD=dawidkrysa

# Networking & Hosting (DuckDNS)
DUCKDNS_SUBDOMAIN=dawidkrysa
DUCKDNS_TOKEN="..."  # your duckDNS token
VIRTUAL_HOST=dawidkrysa.duckdns.org

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=app.py
FLASK_SECRET_KEY="..." # your secret key
```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/dawidkrysa/budget-project.git
   ```
2. Run Docker Compose
   ```sh
   docker compose run -d
   ```
3. Configure [DuckDNS](https://www.duckdns.org/)

4. Configure [Nginx Proxy Manager](https://nginxproxymanager.com/setup/#initial-run)

 <img src="images/nginx-proxy-manager-configuration.png" alt="Nginx Proxy Manager Configuration">

PostgreSQL runs on port `5432`, initialized with schema from `init.sql`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## 📖 Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## ✨ Roadmap

### ✅ Core Features
- [x] Dockerized PostgreSQL + Flask app
- [ ] User authentication (login, registration)
- [ ] Create/read/update/delete (CRUD) for:
  - [ ] Accounts
  - [X] Payees
  - [ ] Categories (with main/sub support)
  - [X] Transactions
  - [ ] Budget assignments per category/month
- [X] Basic dashboard (list of transactions, budget overview)

### 🧱 Backend Tasks
- [X] Flask blueprints for modular code
- [X] PostgreSQL schema (based on ERD)
- [X] Seed scripts for dev setup (`init_data.sql`)
- [X] Use SQLAlchemy

### 💻 Frontend Tasks
- [X] Jinja2 templates using Bootstrap
- [X] Transaction form with validation
- [ ] Monthly budget editor

### 🔄 Budgeting Features
- [ ] Recurring transactions
- [ ] Carry-over category balances
- [ ] Split transactions

### 📈 Reports & Analytics
- [ ] Spending per category/month
- [ ] Budget vs Actual
- [ ] Trends over time

### 📬 User Features
- [ ] Forgot password & reset flow
- [ ] User profile page (change email/name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🧠 Planned Features

See the [open issues](https://github.com/dawidkrysa/budget-project/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **DevOps:** Docker, Docker Compose
- **Frontend:** HTML (Jinja templates, Bootstrap planned)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## 📄 License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## 📬 Contact

Developed by [Dawid Krysa](https://www.linkedin.com/in/dawid-krysa/)
Feel free to reach out via GitHub or LinkedIn.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## 🙏 Acknowledgments

* Inspired by [YNAB](https://www.youneedabudget.com/)
* Flask and Docker documentation



<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[issues-shield]: https://img.shields.io/github/issues/dawidkrysa/budget-project.svg?style=for-the-badge
[issues-url]: https://github.com/dawidkrysa/budget-project/issues
[license-shield]: https://img.shields.io/github/license/dawidkrysa/budget-project.svg?style=for-the-badge
[license-url]: https://github.com/dawidkrysa/budget-project/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/dawid-krysa
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[Docker]: https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[HTML]: https://img.shields.io/badge/html-E34F26?style=for-the-badge&logo=html5&logoColor=white
[HTML-url]: https://www.w3.org/TR/html52/
[CSS]: https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white
[CSS-url]: https://www.w3.org/Style/CSS/
[JavaScript]: https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black


[JavaScript-url]: https://tc39.es/ecma262/