DO
$$
DECLARE
    new_budget_id uuid;
    new_month_id uuid;
    checking_type_id uuid;
    savings_type_id uuid;
    credit_card_type_id uuid;
    groceries_cat_name_id uuid;
    monthly_expenses_group_id uuid;
    groceries_category_id uuid;
    checking_account_id uuid;
    savings_account_id uuid;
    amazon_payee_id uuid;
BEGIN
    -- Insert budget
    INSERT INTO public.budgets (name)
    VALUES ('My Family Budget')
    RETURNING id INTO new_budget_id;

    -- Insert accounts types
    INSERT INTO public.accounts_type (name) VALUES ('Checking') RETURNING id INTO checking_type_id;
    INSERT INTO public.accounts_type (name) VALUES ('Savings') RETURNING id INTO savings_type_id;
    INSERT INTO public.accounts_type (name) VALUES ('Credit Card') RETURNING id INTO credit_card_type_id;

    -- Insert accounts with references to types and budget
    INSERT INTO public.accounts (name, type_id, balance, budget_id)
    VALUES ('My Checking Account', checking_type_id, 2500.00, new_budget_id)
    RETURNING id INTO checking_account_id;

    INSERT INTO public.accounts (name, type_id, balance, budget_id)
    VALUES ('My Savings Account', savings_type_id, 5000.00, new_budget_id)
    RETURNING id INTO savings_account_id;

    -- Insert payee
    INSERT INTO public.payees (name, budget_id)
    VALUES ('Amazon', new_budget_id)
    RETURNING id INTO amazon_payee_id;

    -- Insert category group
    INSERT INTO public.category_groups (name, budget_id)
    VALUES ('Monthly Expenses', new_budget_id)
    RETURNING id INTO monthly_expenses_group_id;

    -- Insert month
    INSERT INTO public.months (month, year, budget_id)
    VALUES (7, 2025, new_budget_id)
    RETURNING id INTO new_month_id;

    -- Insert category name
    INSERT INTO public.category_names (name)
    VALUES ('Groceries')
    RETURNING id INTO groceries_cat_name_id;

    -- Insert category referencing the group, budget, month and category name
    INSERT INTO public.categories (category_group_id, budget_id, month_id, category_name_id)
    VALUES (monthly_expenses_group_id, new_budget_id, new_month_id, groceries_cat_name_id)
    RETURNING id INTO groceries_category_id;

    -- Insert transaction referencing category, account, payee, and budget
    INSERT INTO public.transactions (date, category_id, account_id, payee_id, amount, memo, budget_id)
    VALUES (CURRENT_DATE, groceries_category_id, checking_account_id, amazon_payee_id, -120.50, 'Bought groceries at supermarket', new_budget_id);

END
$$;
