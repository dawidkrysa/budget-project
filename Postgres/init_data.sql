DO
$$
    DECLARE
        new_budget_id uuid;
    BEGIN
        INSERT INTO public.budgets (name)
        VALUES ('My Family Budget')
        RETURNING id INTO new_budget_id;

        INSERT INTO public.accounts_type (name)
        VALUES ('Checking'),
               ('Savings'),
               ('Credit Card');

        INSERT INTO public.accounts (name, type_id, balance, budget_id)
        SELECT 'My Checking Account', t.id, 2500.00, new_budget_id
        FROM public.accounts_type t
        WHERE t.name = 'Checking'
        LIMIT 1;

        INSERT INTO public.accounts (name, type_id, balance, budget_id)
        SELECT 'My Savings Account', t.id, 5000.00, new_budget_id
        FROM public.accounts_type t
        WHERE t.name = 'Savings'
        LIMIT 1;

        INSERT INTO public.payees (name, budget_id)
        VALUES ('Amazon', new_budget_id);

        INSERT INTO public.category_groups (name, budget_id)
        VALUES ('Monthly Expenses', new_budget_id);

        INSERT INTO public.categories (name, category_group_id, budget_id)
        SELECT 'Groceries', cg.id, cg.budget_id
        FROM public.category_groups cg
        WHERE cg.name = 'Monthly Expenses';

        INSERT INTO public.months (month, year, budget_id)
        VALUES (7, 2025, new_budget_id);

        INSERT INTO public.transactions (date, category_id, account_id, payee_id, amount, memo, budget_id)
        SELECT CURRENT_DATE,
               c.id,
               a.id,
               p.id,
               -120.50,
               'Bought groceries at supermarket',
               a.budget_id
        FROM public.categories c
                 JOIN public.accounts a ON a.budget_id = c.budget_id
                 JOIN public.payees p ON p.budget_id = c.budget_id
        LIMIT 1;

        COMMIT;
    END
$$;