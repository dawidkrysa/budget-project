-- ==========================================
-- Accounts
-- ==========================================
CREATE OR REPLACE FUNCTION update_account_balance()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_account_balance ON transactions;
CREATE TRIGGER trg_update_account_balance
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_account_balance();



-- ==========================================
-- Categories
-- ==========================================
CREATE OR REPLACE FUNCTION update_category_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Always recompute activity from transactions
    UPDATE categories
    SET activity = COALESCE((
        SELECT SUM(CASE
            WHEN deleted IS FALSE THEN amount
            ELSE 0
        END)
        FROM transactions
        WHERE category_id = NEW.category_id
    ), 0)
    WHERE id = NEW.category_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_category_activity ON transactions;
CREATE TRIGGER trg_update_category_activity
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_category_activity();



-- ==========================================
-- Months
-- ==========================================
CREATE OR REPLACE FUNCTION update_month_activity()
RETURNS TRIGGER AS $$
DECLARE
    v_month INT := EXTRACT(MONTH FROM COALESCE(NEW.date, OLD.date));
    v_year  INT := EXTRACT(YEAR  FROM COALESCE(NEW.date, OLD.date));
BEGIN
    -- Always recompute activity from transactions
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

    -- Always update to_be_budgeted
    UPDATE months
    SET to_be_budgeted = budgeted - activity
    WHERE month = v_month AND year = v_year;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_month_activity ON transactions;
CREATE TRIGGER trg_update_month_activity
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_month_activity();



-- ==========================================
-- Category balance (budget - activity)
-- ==========================================
CREATE OR REPLACE FUNCTION update_category_balance()
RETURNS TRIGGER AS $$
BEGIN
    NEW.balance := COALESCE(NEW.budgeted,0) + COALESCE(NEW.activity,0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_category_balance ON categories;
CREATE TRIGGER trg_update_category_balance
BEFORE INSERT OR UPDATE ON categories
FOR EACH ROW
EXECUTE FUNCTION update_category_balance();

UPDATE transactions SET id = id;
UPDATE categories SET id = id;