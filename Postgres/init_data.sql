-- Import accounts
INSERT INTO accounts (name, hidden) VALUES ('Bank A', false);
INSERT INTO accounts (name, hidden) VALUES ('Bank B', false);
INSERT INTO accounts (name, hidden) VALUES ('Bank C', false);
INSERT INTO accounts (name, hidden) VALUES ('Obligacje Skarbowe', false);
INSERT INTO accounts (name, hidden) VALUES ('Obligacje Emerytalne', false);

-- Import main categories
INSERT INTO categories (name, hidden) VALUES ('Oszczędności', false);
INSERT INTO categories (name, hidden) VALUES ('Potrzeby', false);
INSERT INTO categories (name, hidden) VALUES ('Firma', false);
INSERT INTO categories (name, hidden) VALUES ('Zachcianki', false);
INSERT INTO categories (name, hidden) VALUES ('Okresowe Wydatki', false);

-- Import subcategories
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Fundusz Awaryjny', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Zaliczka', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Portfel Długoterminowy', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Czynsz i Media', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Zakupy Spożywcze', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Internet', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Telefon', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Transport', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Serwisy Streamingowe', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Kosmetyki, Drogeria i Środki Czystości', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Nieprzewidziane Wydatki', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Leasing', (SELECT Id FROM categories WHERE Name = 'Firma'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Księgowy', (SELECT Id FROM categories WHERE Name = 'Firma'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Kredyt Gotówkowy', (SELECT Id FROM categories WHERE Name = 'Firma'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Fryzjer', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Ubrania', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Jedzenie na Mieście', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Inne', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Urodziny', (SELECT Id FROM categories WHERE Name = 'Okresowe Wydatki'), true);

INSERT INTO budget (month, year, assigned, category_id)  SELECT 1,2024,0,Id FROM categories WHERE main_category_id IS NOT NULL;
INSERT INTO budget (month, year, assigned, category_id)  SELECT 1,2025,0,Id FROM categories WHERE main_category_id IS NOT NULL;

INSERT INTO payees (name) VALUES
('Supermarket XYZ'),
('Warzywniak u Ani'),
('Stacja Paliw Shell'),
('Netflix'),
('Restauracja La Pasta'),
('Wspólnota Mieszkaniowa'),
('Kino Helios'),
('Księgarnia BookHouse'),
('Operator GSM'),
('Warsztat AutoFix');

INSERT INTO transactions (date, amount, category_id, account_id, memo, payee_id) VALUES
('2024-01-02', 150.00, 1, 1, 'Zakupy spożywcze', 1),
('2024-01-05', 50.00, 1, 2, 'Warzywa i owoce', 2),
('2024-01-08', 200.00, 2, 1, 'Paliwo', 3),
('2024-01-12', 100.00, 3, 3, 'Subskrypcja Netflix', 4),
('2024-01-15', 75.00, 1, 2, 'Kolacja na mieście', 5),
('2024-01-18', 500.00, 4, 1, 'Czynsz', 6),
('2024-01-22', 60.00, 2, 2, 'Bilet do kina', 7),
('2024-01-25', 120.00, 5, 3, 'Zakup książek', 8),
('2024-01-28', 90.00, 3, 1, 'Abonament telefoniczny', 9),
('2024-01-31', 300.00, 6, 2, 'Naprawa samochodu', 10);


