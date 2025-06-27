CREATE TABLE IF NOT EXISTS accounts
(
  id     integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name   text    NOT NULL UNIQUE,
  hidden boolean DEFAULT false
);

CREATE TABLE IF NOT EXISTS categories
(
  id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name             text    NOT NULL UNIQUE,
  main_category_id integer,
  hidden           boolean DEFAULT false,
  CONSTRAINT FK_main_category FOREIGN KEY (main_category_id) REFERENCES categories (id)
);

CREATE TABLE IF NOT EXISTS budget
(
  id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  month       integer NOT NULL,
  year        integer NOT NULL,
  assigned      decimal(15,2) NOT NULL,
  category_id integer NOT NULL,
  CONSTRAINT FK_categories_TO_budget FOREIGN KEY (category_id) REFERENCES categories (id)
);

CREATE TABLE IF NOT EXISTS payees
(
  id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text   NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS transactions
(
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date        date          NOT NULL,
  amount      decimal(15,2) NOT NULL,
  category_id integer,
  account_id  integer       NOT NULL,
  memo        text,
  payee_id    bigint        NOT NULL,
  CONSTRAINT FK_categories_TO_transactions FOREIGN KEY (category_id) REFERENCES categories (id),
  CONSTRAINT FK_accounts_TO_transactions FOREIGN KEY (account_id) REFERENCES accounts (id),
  CONSTRAINT FK_payees_TO_transactions FOREIGN KEY (payee_id) REFERENCES payees (id)
);

CREATE TABLE IF NOT EXISTS users
(
  id   bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  login text   NOT NULL UNIQUE,
  password text   NOT NULL,
  active boolean DEFAULT false,
  email text NOT NULL UNIQUE,
  CONSTRAINT email_check CHECK (email LIKE '%_@__%.__%'),
  name text NOT NULL,
  CONSTRAINT name_check CHECK (name != '')
);

-- Create a view that shows the account name and the sum of all transactions for that account.
-- The view should only include transactions that are not hidden and categories that are not hidden.
-- The view should be ordered by account name.
CREATE OR REPLACE VIEW accounts_view AS
SELECT a.name as account_name, COALESCE(SUM(t.amount), 0) as total FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN categories mc ON c.main_category_id = mc.id
LEFT JOIN payees p ON t.payee_id = p.id
WHERE (c.hidden = false OR c.hidden IS NULL) 
    AND (mc.hidden = false OR mc.hidden IS NULL)
    AND (a.hidden = false OR a.hidden IS NULL)
GROUP BY a.id, a.name
ORDER BY a.name;

-- Create a view that shows the category name, the main category name, and the total amount spent in that category.
-- The view should only include categories that are not hidden and main categories that are not hidden.
-- The view should be ordered by the category name.
CREATE OR REPLACE VIEW categories_view AS
SELECT mc.name as main_category_name, c.name as category_name, SUM(t.amount) as total FROM transactions t
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN categories mc ON c.main_category_id = mc.id
LEFT JOIN payees p ON t.payee_id = p.id
LEFT JOIN accounts a ON t.account_id = a.id
WHERE (c.hidden = false OR c.hidden IS NULL) 
  AND (mc.hidden = false OR mc.hidden IS NULL)
  AND (a.hidden = false OR a.hidden IS NULL)
GROUP BY t.category_id, mc.name, c.name
ORDER BY mc.name, c.name;

-- Create a view called budget_report that shows available budget for each category in each month of each year.
CREATE OR REPLACE VIEW budget_report AS
SELECT  b.month, b.year, mc.name as main_category, c.name AS category,
    b.assigned, COALESCE(SUM(t.amount), 0) AS activty,
    b.assigned - COALESCE(SUM(t.amount), 0) AS available
FROM budget b
LEFT JOIN transactions t ON b.category_id = t.category_id 
    AND EXTRACT(YEAR FROM t.date) = b.year 
    AND EXTRACT(MONTH FROM t.date) = b.month
JOIN categories c ON b.category_id = c.id
JOIN categories mc ON c.main_category_id = mc.id
GROUP BY b.month, b.year, mc.name, c.name, b.assigned
ORDER BY b.month, b.year, mc.name, c.name, b.assigned

-- Create a view that shows all transactions with their account, payee, category, memo, and amount.
CREATE OR REPLACE VIEW transactions_view AS
SELECT
    t.date, a.name as account_name, p.name as payee_name, c.name as category_name, t.memo, t.amount
FROM transactions t
JOIN categories c ON t.category_id = c.id
JOIN payees p ON t.payee_id = p.id
JOIN accounts a ON t.account_id = a.id