
CREATE TABLE Question_Info (
    id INT NOT NULL,
    sas_var_name VARCHAR(8) NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (id),
	UNIQUE (sas_var_name)
);

CREATE TABLE User_Answers (
    id INT NOT NULL,
    user_id INT NOT NULL,
    question_id INT NOT NULL,
    val INT NOT NULL,
	FOREIGN KEY (question_id) REFERENCES Question_Info (id),
    PRIMARY KEY (id),
	UNIQUE (user_id, question_id)
);


CREATE TABLE Question_Values (
    id INT NOT NULL,
    question_id INT  NOT NULL,
    answer_label TEXT  NOT NULL,
    answer_value REAL NOT NULL,
    FOREIGN KEY (question_id) REFERENCES Question_Info (id),
    PRIMARY KEY (id),
    UNIQUE (question_id, answer_value)
    
);
