CREATE TABLE public.tickets (
	id serial4 NOT NULL,
	client_id VARCHAR(20) NOT NULL,
	title varchar(255) NOT NULL,
	description text NULL,
	status_id int4 NULL,
	priority_id int4 NULL,
	category_id int4 NULL,
	creator_id int4 NULL,
	assignee_id int4 NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT tickets_pkey PRIMARY KEY (id),
	CONSTRAINT tickets_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES public.usuarios(id) ON DELETE SET NULL,
	CONSTRAINT tickets_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.ticket_categories(id) ON DELETE SET NULL,
	CONSTRAINT tickets_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.usuarios(id) ON DELETE CASCADE,
	CONSTRAINT tickets_priority_id_fkey FOREIGN KEY (priority_id) REFERENCES public.ticket_priorities(id) ON DELETE RESTRICT,
	CONSTRAINT tickets_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.ticket_status(id) ON DELETE RESTRICT
);