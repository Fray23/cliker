DO $$
    BEGIN
    IF NOT EXISTS (
            SELECT FROM information_schema.tables
            WHERE  table_name = 'tasks'
    ) THEN
        CREATE TABLE tasks (
           task_id serial PRIMARY KEY,
           profile VARCHAR (128) NOT NULL,
           number_of_posts integer CHECK (number_of_posts > 0),
           hostname VARCHAR (128) NOT NULL,
           created_on TIMESTAMP NOT NULL,
           time_taking_to_work TIMESTAMP,
           time_finish TIMESTAMP,
           status VARCHAR (128) NOT NULL
        );
    END IF;

    IF NOT EXISTS (
            SELECT FROM information_schema.tables
            WHERE  table_name = 'posts'
    ) THEN
        CREATE TABLE posts (
            id serial PRIMARY KEY,
            post_url VARCHAR (255) NOT NULL,
            number_of_likes integer CHECK (number_of_likes > 0),
            post_created_on TIMESTAMP
        );
    END IF;

    
END $$;
