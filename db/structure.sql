SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA IF NOT EXISTS public;


CREATE TABLE public.image_batches
(
    id              integer                     NOT NULL,
    content_image   bytea                       NOT NULL,
    style_image     bytea                       NOT NULL,
    generated_image bytea                       NOT NULL,
    processed_at    timestamp without time zone,
    created_at      timestamp without time zone NOT NULL,
    updated_at      timestamp without time zone NOT NULL
);


CREATE TABLE public.image_batch_training_iteration_samples
(
    id              integer NOT NULL,
    image_batch_id  integer NOT NULL,
    generated_image bytea   NOT NULL
);


ALTER TABLE ONLY public.image_batches
    ADD CONSTRAINT image_batches_pkey PRIMARY KEY (id);


ALTER TABLE ONLY public.image_batch_training_iteration_samples
    ADD CONSTRAINT image_batch_training_iteration_samples_pkey PRIMARY KEY (id);


CREATE SEQUENCE public.image_batches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE SEQUENCE public.image_batch_training_iteration_samples_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.image_batches_id_seq OWNED BY public.image_batches.id;


ALTER SEQUENCE public.image_batch_training_iteration_samples_id_seq OWNED BY public.image_batch_training_iteration_samples.id;


ALTER TABLE ONLY public.image_batch_training_iteration_samples
    ADD CONSTRAINT fk__image_batch_training_iteration_samples__image_batches FOREIGN KEY (image_batch_id) REFERENCES public.image_batches (id) ON DELETE CASCADE;
