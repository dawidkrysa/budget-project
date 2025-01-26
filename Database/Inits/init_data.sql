-- Import accounts
INSERT INTO accounts (name, hidden) VALUES ('Mbank', false);
INSERT INTO accounts (name, hidden) VALUES ('Mbank firmowe', false);
INSERT INTO accounts (name, hidden) VALUES ('PKO', false);
INSERT INTO accounts (name, hidden) VALUES ('Obligacje skarbowe', false);
INSERT INTO accounts (name, hidden) VALUES ('IKZE - Obligacje', false);

-- Import main categories
INSERT INTO categories (name, hidden) VALUES ('Oszczędności', false);
INSERT INTO categories (name, hidden) VALUES ('Potrzeby', false);
INSERT INTO categories (name, hidden) VALUES ('Firma', false);
INSERT INTO categories (name, hidden) VALUES ('Zachcianki', false);
INSERT INTO categories (name, hidden) VALUES ('Okresowe wydatki', false);

-- Import subcategories
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Poduszka finansowa', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Wkład własny', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Portfel długoterminowy', (SELECT Id FROM categories WHERE Name = 'Oszczędności'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Najem i media', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Zakupy spożywcze', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Internet', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Telefon', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Transport', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Serwisy streamingowe', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Kosmetyki, drogera i środki czystości', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Nieprzewidziane wydatki', (SELECT Id FROM categories WHERE Name = 'Potrzeby'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Leasing', (SELECT Id FROM categories WHERE Name = 'Firma'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Księgowy', (SELECT Id FROM categories WHERE Name = 'Firma'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Kredyt gotówkowy', (SELECT Id FROM categories WHERE Name = 'Firma'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Fryzjer', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Ubrania', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Jedzenie na mieście', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);
INSERT INTO categories (name, main_category_id, hidden) VALUES ('Inne', (SELECT Id FROM categories WHERE Name = 'Zachcianki'), false);

INSERT INTO categories (name, main_category_id, hidden) VALUES ('Urodziny', (SELECT Id FROM categories WHERE Name = 'Okresowe wydatki'), true);

INSERT INTO budget (month, year, amount, category_id)  SELECT 1,2025,0,Id FROM categories;



