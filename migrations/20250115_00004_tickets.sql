CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status_id INT REFERENCES ticket_status(id) ON DELETE RESTRICT,
    priority_id INT REFERENCES ticket_priorities(id) ON DELETE RESTRICT,
    category_id INT REFERENCES ticket_categories(id) ON DELETE SET NULL,
    creator_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
    assignee_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);