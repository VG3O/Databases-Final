CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(40) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS special_chud(
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    description_of_chud TEXT
);

INSERT INTO users (user_name, email) VALUES
    ('hoose', 'smoose@huh.com'),
    ('vg3o', 'bruh@email.com'),
    ('holdin_mcgroin', 'email@connor.com'),
    ('bigManSees', 'newguy@email.com'),
    ('hasbro', 'feeder@deadlock.com'),
    ('kai', 'farts@strigid.co'),
    ('xepois', 'stupid@strigid.co'),
    ('jeffery cheeseburger', 'jeffbogo@strigid.co'),
    ('mylo', 'fish@mail.com'),
    ('fifth guy burger', 'burger@mail.com')
ON CONFLICT (email) DO NOTHING;

INSERT INTO special_chud (user_id, description_of_chud) VALUES
    (5, 'Love you pwetril');