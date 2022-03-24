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


--
-- Name: session_type; Type: ENUM; Schema: public; Owner: -
--

CREATE TYPE public.session_type AS ENUM ('user', 'presentation');


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sessions
(
    id   serial              NOT NULL,
    uuid uuid                NOT NULL,
    type public.session_type NOT NULL
);


--
-- Name: scheduled_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scheduled_images
(
    id              serial  NOT NULL,
    user_session_id integer NOT NULL,
    content_image   bytea   NOT NULL,
    style_image     bytea   NOT NULL
);


--
-- Name: processed_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.processed_images
(
    id                      serial                      NOT NULL,
    presentation_session_id integer                     NOT NULL,
    scheduled_image_id      integer                     NOT NULL,
    generated_image         bytea                       NOT NULL,
    presented               bool DEFAULT false,
    created_at              timestamp without time zone NOT NULL
);


--
-- Name: sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: scheduled_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_images
    ADD CONSTRAINT scheduled_images_pkey PRIMARY KEY (id);


--
-- Name: processed_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_images
    ADD CONSTRAINT processed_images_pkey PRIMARY KEY (id);


--
-- Name: fk__scheduled_images__sessions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scheduled_images
    ADD CONSTRAINT fk__scheduled_images__sessions
        FOREIGN KEY (user_session_id)
            REFERENCES public.sessions (id) ON DELETE CASCADE;


--
-- Name: fk__processed_images__scheduled_images; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_images
    ADD CONSTRAINT fk__processed_images__scheduled_images
        FOREIGN KEY (scheduled_image_id)
            REFERENCES public.scheduled_images (id) ON DELETE CASCADE;


--
-- Name: fk__processed_images__sessions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.processed_images
    ADD CONSTRAINT fk__processed_images__sessions
        FOREIGN KEY (presentation_session_id)
            REFERENCES public.sessions (id) ON DELETE CASCADE;


--
-- Name: idx_sessions_type_uuid; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_sessions_type_uuid ON public.sessions (type, uuid);


--
-- Name: idx_processed_images_scheduled_image_id_presentation_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_processed_images_scheduled_image_id_presentation_session_id
    ON public.processed_images (scheduled_image_id, presentation_session_id);


--
-- Name: idx_processed_images_presented; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_processed_images_presented ON public.processed_images (presented);