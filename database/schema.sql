-- NOTE: NOT THE ORIGINAL!!!! DON'T USE AS MASTER COPY

CREATE TABLE question_info (
    id SERIAL,
    var_name VARCHAR(8) NOT NULL,
    label TEXT NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (var_name)
);

CREATE TABLE user_answers (
    id SERIAL,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    val INT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES question_info (id),
    PRIMARY KEY (id),
    UNIQUE (user_id, question_id)
);

CREATE TABLE question_values (
    id SERIAL,
    question_id INT  NOT NULL,
    label TEXT  NOT NULL,
    value REAL,
    value_end REAL, -- if NULL, not relevant
    FOREIGN KEY (question_id) REFERENCES question_info (id),
    PRIMARY KEY (id),
    UNIQUE (question_id, value)
);