BEGIN;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


CREATE TABLE IF NOT EXISTS public.accounts
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    name text COLLATE pg_catalog."default" NOT NULL,
    type_id uuid,
    deleted boolean DEFAULT false,
    balance numeric(15, 2),
    transfer_payee_id uuid,
    budget_id uuid NOT NULL,
    CONSTRAINT accounts_pkey PRIMARY KEY (id),
    CONSTRAINT accounts_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.months
(
    month integer NOT NULL,
    year integer NOT NULL,
    budgeted numeric(15, 2) NOT NULL DEFAULT 0,
    activity numeric(15, 2) NOT NULL DEFAULT 0,
    to_be_budgeted numeric(15, 2) NOT NULL DEFAULT 0,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    CONSTRAINT budget_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.categories
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    name text COLLATE pg_catalog."default" NOT NULL,
    category_group_id uuid NOT NULL,
    hidden boolean DEFAULT false,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    budgeted numeric(15, 2) NOT NULL DEFAULT 0,
    activity numeric(15, 2) NOT NULL DEFAULT 0,
    balance numeric(15, 2) NOT NULL DEFAULT 0,
    CONSTRAINT categories_pkey PRIMARY KEY (id),
    CONSTRAINT categories_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.payees
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    name text COLLATE pg_catalog."default" NOT NULL,
    transfer_account_id uuid,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    CONSTRAINT payees_pkey PRIMARY KEY (id),
    CONSTRAINT payees_name_key UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS public.transactions
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    date date NOT NULL,
    category_id uuid,
    account_id uuid NOT NULL,
    payee_id bigint NOT NULL,
    amount numeric(15, 2) NOT NULL,
    memo text COLLATE pg_catalog."default",
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    CONSTRAINT transactions_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.users
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    login text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    active boolean DEFAULT false,
    email text COLLATE pg_catalog."default" NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_login_key UNIQUE (login)
);

CREATE TABLE IF NOT EXISTS public."accountsType"
(
    id uuid,
    name text NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.budgets
(
    id uuid,
    name text,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.category_groups
(
    id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    name text COLLATE pg_catalog."default" NOT NULL,
    deleted boolean DEFAULT false,
    budget_id uuid NOT NULL,
    CONSTRAINT categories_pkey PRIMARY KEY (id),
    CONSTRAINT categories_name_key UNIQUE (name)
);

ALTER TABLE IF EXISTS public.accounts
    ADD FOREIGN KEY (id)
    REFERENCES public.transactions (account_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;


ALTER TABLE IF EXISTS public.categories
    ADD FOREIGN KEY (id)
    REFERENCES public.transactions (category_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;


ALTER TABLE IF EXISTS public.payees
    ADD FOREIGN KEY (transfer_account_id)
    REFERENCES public.accounts (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;


ALTER TABLE IF EXISTS public.payees
    ADD FOREIGN KEY (id)
    REFERENCES public.transactions (payee_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;


ALTER TABLE IF EXISTS public."accountsType"
    ADD FOREIGN KEY (id)
    REFERENCES public.accounts (type_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.payees (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.accounts (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.transactions (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.categories (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.category_groups (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.budgets
    ADD FOREIGN KEY (id)
    REFERENCES public.months (budget_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE CASCADE
    NOT VALID;


ALTER TABLE IF EXISTS public.category_groups
    ADD FOREIGN KEY (id)
    REFERENCES public.categories (category_group_id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE SET NULL
    NOT VALID;

END;