CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(30) NOT NULL UNIQUE,
    password VARCHAR(30) NOT NULL,
    email VARCHAR(40) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO users (user_name, email, password) VALUES
    ('hoose', 'smoose@huh.com', 'tylersnot'),
    ('vg3o', 'bruh@email.com', 'brandoneLol'),
    ('holdin_mcgroin', 'email@connor.com', 'ronnocRile'),
    ('bigManSees', 'newguy@email.com', 'smallMan1234'),
    ('hasbro', 'feeder@deadlock.com', 'hazlett'),
    ('kai', 'kai@strigid.co', 'evilCeoMoment'),
    ('xepois', 'british@strigid.co', 'programmingInBrish'),
    ('jeffery cheeseburger', 'jeffbogo@strigid.co', 'Cheesbogo_2'),
    ('mylo', 'fish@mail.com', '1mylo1mylo'),
    ('fifth guy burger', 'burger@mail.com', 'FourthDudeBurger')
ON CONFLICT (email) DO NOTHING;

INSERT INTO channels (name) 
VALUES ('general'), ('gaming'), ('off-topic') 
ON CONFLICT (name) DO NOTHING;