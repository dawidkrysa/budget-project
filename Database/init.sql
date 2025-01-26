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
    category_id int      NOT NULL
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
    category_id int,
    account_id  int,
    memo       text
);

ALTER TABLE budget
    ADD CONSTRAINT FK_categories_TO_budget
        FOREIGN KEY (category_id)
        REFERENCES categories (id);

ALTER TABLE transactions
    ADD CONSTRAINT FK_categories_TO_transactions
        FOREIGN KEY (category_id)
        REFERENCES categories (id);

ALTER TABLE transactions
    ADD CONSTRAINT FK_accounts_TO_transactions
        FOREIGN KEY (account_id)
        REFERENCES accounts (id);

-- Create budget view
CREATE OR REPLACE VIEW budget_view AS SELECT b.month, b.year, b.amount, mc.name as main_category_name, c.name as category_name
FROM budget b 
JOIN categories c ON b.category_id = c.id
JOIN categories mc ON c.main_category_id = mc.id
WHERE mc.hidden = false AND c.hidden = false;
