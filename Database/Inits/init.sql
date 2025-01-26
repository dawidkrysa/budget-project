CREATE TABLE accounts
(
    id     SERIAL PRIMARY KEY,
    name   text    NOT NULL,
    hidden boolean
);

CREATE TABLE budget
(
    id          SERIAL PRIMARY KEY,
    month       int      NOT NULL,
    year        int      NOT NULL,
    amount      DECIMAL(15,2) NOT NULL,
    categories_id int      NOT NULL
);

CREATE TABLE categories
(
    id               SERIAL PRIMARY KEY,
    name             text    NOT NULL,
    main_category_id int,
    hidden           boolean
);

CREATE TABLE transactions
(
    id          SERIAL PRIMARY KEY,
    date        date          NOT NULL,
    amount      DECIMAL(15,2) NOT NULL,
    category_id int           NOT NULL,
    account_id  int           NOT NULL
);

ALTER TABLE budget
    ADD CONSTRAINT FK_categories_TO_budget
        FOREIGN KEY (categories_id)
        REFERENCES categories (id);

ALTER TABLE transactions
    ADD CONSTRAINT FK_categories_TO_transactions
        FOREIGN KEY (categories_id)
        REFERENCES categories (id);

ALTER TABLE transactions
    ADD CONSTRAINT FK_accounts_TO_transactions
        FOREIGN KEY (account_id)
        REFERENCES accounts (id);