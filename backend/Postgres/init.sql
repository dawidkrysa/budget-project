CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;

CREATE FUNCTION public.update_account_balance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Always recompute from transactions
    UPDATE accounts
    SET balance = COALESCE((
        SELECT SUM(CASE
            WHEN deleted IS FALSE THEN amount
            ELSE 0
        END)
        FROM transactions
        WHERE account_id = NEW.account_id
    ), 0)
    WHERE id = NEW.account_id;

    RETURN NEW;
END;
$$;

CREATE FUNCTION public.update_category_activity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Always recompute activity from transactions
    UPDATE categories
    SET activity = COALESCE((
        SELECT SUM(CASE
            WHEN t.deleted IS FALSE THEN t.amount
            ELSE 0
        END)
        FROM transactions t
        JOIN months m ON EXTRACT(MONTH FROM t.date) = m.month AND EXTRACT(YEAR FROM t.date) = m.year
        WHERE t.category_id = NEW.category_id
          AND m.id = categories.month_id
    ), 0)
    WHERE id = NEW.category_id
      AND month_id = (SELECT id FROM months WHERE month = EXTRACT(MONTH FROM NEW.date)
                                            AND year = EXTRACT(YEAR FROM NEW.date));

    RETURN NEW;
END;
$$;

CREATE FUNCTION public.update_category_balance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.balance := COALESCE(NEW.budgeted,0) + COALESCE(NEW.activity,0);
    RETURN NEW;
END;
$$;

CREATE FUNCTION public.update_category_balance_transaction() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE categories
        SET activity = activity + NEW.amount
        WHERE id = NEW.category_id;

    ELSE
        UPDATE categories
        SET activity = activity - OLD.amount
        WHERE id = OLD.category_id;

        IF TG_OP = 'UPDATE' AND NEW.deleted IS FALSE THEN
            UPDATE categories
            SET activity = activity + NEW.amount
            WHERE id = NEW.category_id;
        END IF;

        UPDATE categories
        SET balance = budgeted - activity
        WHERE id = OLD.category_id;

    END IF;

    UPDATE categories
    SET balance = budgeted - activity
    WHERE id = NEW.category_id;

    RETURN NEW;
END;
$$;

CREATE FUNCTION public.update_month_activity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_month INT := EXTRACT(MONTH FROM COALESCE(NEW.date, OLD.date));
    v_year  INT := EXTRACT(YEAR  FROM COALESCE(NEW.date, OLD.date));
BEGIN
    UPDATE months
    SET activity = COALESCE((
        SELECT SUM(CASE
            WHEN deleted IS FALSE THEN amount
            ELSE 0
        END)
        FROM transactions
        WHERE EXTRACT(MONTH FROM date) = v_month
          AND EXTRACT(YEAR FROM date) = v_year
    ), 0)
    WHERE month = v_month AND year = v_year;

    UPDATE months
    SET to_be_budgeted = budgeted - activity
    WHERE month = v_month AND year = v_year;

    RETURN NEW;
END;
$$;

CREATE FUNCTION public.update_month_balance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE months
        SET activity = activity + NEW.amount
        WHERE month = EXTRACT(MONTH FROM NEW.date)
          AND year = EXTRACT(YEAR FROM NEW.date);

    ELSE
        UPDATE months
        SET activity = activity - OLD.amount
        WHERE month = EXTRACT(MONTH FROM OLD.date)
          AND year = EXTRACT(YEAR FROM OLD.date);

        IF TG_OP = 'UPDATE' AND NEW.deleted IS FALSE THEN
            UPDATE months
            SET activity = activity + NEW.amount
            WHERE month = EXTRACT(MONTH FROM NEW.date)
              AND year = EXTRACT(YEAR FROM NEW.date);
        END IF;

        UPDATE months
        SET to_be_budgeted = budgeted - activity
        WHERE month = EXTRACT(MONTH FROM NEW.date)
          AND year = EXTRACT(YEAR FROM NEW.date);

    END IF;

    UPDATE months
    SET to_be_budgeted = budgeted - activity
    WHERE month = EXTRACT(MONTH FROM NEW.date)
      AND year = EXTRACT(YEAR FROM NEW.date);

    RETURN NEW;
END;
$$;

CREATE TABLE public.accounts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    type_id uuid,
    deleted boolean DEFAULT false,
    balance numeric(15,2),
    transfer_payee_id uuid,
    budget_id uuid NOT NULL
);

CREATE TABLE public."accountsType" (
    id character varying(36) NOT NULL,
    name text NOT NULL
);

CREATE TABLE public.accounts_type (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL
);

CREATE TABLE public.budgets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL
);

CREATE TABLE public.categories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    category_group_id uuid NOT NULL,
    hidden boolean DEFAULT false,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    budgeted numeric(15,2) DEFAULT 0 NOT NULL,
    activity numeric(15,2) DEFAULT 0 NOT NULL,
    balance numeric(15,2) DEFAULT 0 NOT NULL,
    month_id uuid NOT NULL,
    category_name_id uuid NOT NULL
);

CREATE TABLE public.category_groups (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL
);

CREATE TABLE public.category_names (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL
);

CREATE TABLE public.months (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    budgeted numeric(15,2) DEFAULT 0 NOT NULL,
    activity numeric(15,2) DEFAULT 0 NOT NULL,
    to_be_budgeted numeric(15,2) DEFAULT 0 NOT NULL,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL
);

CREATE TABLE public.payees (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    transfer_account_id uuid,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL
);

CREATE TABLE public.transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    date date NOT NULL,
    category_id uuid,
    account_id uuid NOT NULL,
    payee_id uuid NOT NULL,
    amount numeric(15,2) NOT NULL,
    memo text,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL
);

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    active boolean DEFAULT false,
    email text NOT NULL,
    name text NOT NULL
);

ALTER TABLE ONLY public."accountsType"
    ADD CONSTRAINT "accountsType_pkey" PRIMARY KEY (id);

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_name_key UNIQUE (name);

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.accounts_type
    ADD CONSTRAINT accounts_type_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.budgets
    ADD CONSTRAINT budgets_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.category_groups
    ADD CONSTRAINT category_groups_name_key UNIQUE (name);

ALTER TABLE ONLY public.category_groups
    ADD CONSTRAINT category_groups_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.category_names
    ADD CONSTRAINT category_names_name_key UNIQUE (name);

ALTER TABLE ONLY public.category_names
    ADD CONSTRAINT category_names_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.months
    ADD CONSTRAINT months_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.payees
    ADD CONSTRAINT payees_name_key UNIQUE (name);

ALTER TABLE ONLY public.payees
    ADD CONSTRAINT payees_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

CREATE TRIGGER trg_update_account_balance AFTER INSERT OR DELETE OR UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.update_account_balance();

CREATE TRIGGER trg_update_category_activity AFTER INSERT OR DELETE OR UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.update_category_activity();

CREATE TRIGGER trg_update_category_balance BEFORE INSERT OR UPDATE ON public.categories FOR EACH ROW EXECUTE FUNCTION public.update_category_balance();

CREATE TRIGGER trg_update_month_activity AFTER INSERT OR DELETE OR UPDATE ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.update_month_activity();

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.accounts_type(id);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_category_group_id_fkey FOREIGN KEY (category_group_id) REFERENCES public.category_groups(id);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_month_id_fkey FOREIGN KEY (month_id) REFERENCES public.months(id) ON DELETE SET NULL NOT VALID;

ALTER TABLE ONLY public.category_groups
    ADD CONSTRAINT category_groups_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT fk_category_name FOREIGN KEY (category_name_id) REFERENCES public.category_names(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY public.months
    ADD CONSTRAINT months_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.payees
    ADD CONSTRAINT payees_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.payees
    ADD CONSTRAINT payees_transfer_account_id_fkey FOREIGN KEY (transfer_account_id) REFERENCES public.accounts(id);

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.accounts(id);

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_budget_id_fkey FOREIGN KEY (budget_id) REFERENCES public.budgets(id);

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_payee_id_fkey FOREIGN KEY (payee_id) REFERENCES public.payees(id);
