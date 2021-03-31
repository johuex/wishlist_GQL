--
-- PostgreSQL database dump
--

-- Dumped from database version 12.5
-- Dumped by pg_dump version 12.6

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: degree_of_desire; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.degree_of_desire (
    item_id integer NOT NULL,
    degree character varying(50) NOT NULL
);


ALTER TABLE public.degree_of_desire OWNER TO johuex;

--
-- Name: friend_requests; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.friend_requests (
    user_id_from integer NOT NULL,
    user_id_to integer NOT NULL
);


ALTER TABLE public.friend_requests OWNER TO johuex;

--
-- Name: friendship; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.friendship (
    user_id_1 integer NOT NULL,
    user_id_2 integer NOT NULL
);


ALTER TABLE public.friendship OWNER TO johuex;

--
-- Name: group; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public."group" (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    about character varying(1000),
    date timestamp with time zone NOT NULL
);


ALTER TABLE public."group" OWNER TO johuex;

--
-- Name: group_id_seq; Type: SEQUENCE; Schema: public; Owner: johuex
--

CREATE SEQUENCE public.group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.group_id_seq OWNER TO johuex;

--
-- Name: group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: johuex
--

ALTER SEQUENCE public.group_id_seq OWNED BY public."group".id;


--
-- Name: group_list; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.group_list (
    group_id integer NOT NULL,
    list_id integer NOT NULL
);


ALTER TABLE public.group_list OWNER TO johuex;

--
-- Name: group_user; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.group_user (
    group_id integer NOT NULL,
    user_id integer NOT NULL,
    role_in_group integer
);


ALTER TABLE public.group_user OWNER TO johuex;

--
-- Name: item; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.item (
    id integer NOT NULL,
    title character varying(50) NOT NULL,
    about character varying(255),
    access_level integer NOT NULL,
    status integer NOT NULL,
    giver_id integer,
    date_creation date NOT NULL,
    date_for_status date
);


ALTER TABLE public.item OWNER TO johuex;

--
-- Name: item_group; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.item_group (
    group_id integer NOT NULL,
    item_id integer NOT NULL
);


ALTER TABLE public.item_group OWNER TO johuex;

--
-- Name: item_id_seq; Type: SEQUENCE; Schema: public; Owner: johuex
--

CREATE SEQUENCE public.item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.item_id_seq OWNER TO johuex;

--
-- Name: item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: johuex
--

ALTER SEQUENCE public.item_id_seq OWNED BY public.item.id;


--
-- Name: item_list; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.item_list (
    list_id integer NOT NULL,
    item_id integer NOT NULL
);


ALTER TABLE public.item_list OWNER TO johuex;

--
-- Name: item_picture; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.item_picture (
    item_id integer NOT NULL,
    path_to_picture integer NOT NULL
);


ALTER TABLE public.item_picture OWNER TO johuex;

--
-- Name: user_item; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.user_item (
    user_id integer NOT NULL,
    item_id integer NOT NULL
);


ALTER TABLE public.user_item OWNER TO johuex;

--
-- Name: users; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.users (
    id integer NOT NULL,
    phone_number character varying(20),
    username character varying(50) NOT NULL,
    surname character varying(50),
    userpic text,
    about character varying(1000),
    birthday date,
    password_hash text NOT NULL,
    nickname character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    token text,
    token_expiration timestamp with time zone,
    last_seen timestamp with time zone
);


ALTER TABLE public.users OWNER TO johuex;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: johuex
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO johuex;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: johuex
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wishlist; Type: TABLE; Schema: public; Owner: johuex
--

CREATE TABLE public.wishlist (
    id integer NOT NULL,
    user_id integer NOT NULL,
    title character varying(50) NOT NULL,
    about character varying(255),
    access_level integer NOT NULL
);


ALTER TABLE public.wishlist OWNER TO johuex;

--
-- Name: wishlist_id_seq; Type: SEQUENCE; Schema: public; Owner: johuex
--

CREATE SEQUENCE public.wishlist_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wishlist_id_seq OWNER TO johuex;

--
-- Name: wishlist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: johuex
--

ALTER SEQUENCE public.wishlist_id_seq OWNED BY public.wishlist.id;


--
-- Name: group id; Type: DEFAULT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public."group" ALTER COLUMN id SET DEFAULT nextval('public.group_id_seq'::regclass);


--
-- Name: item id; Type: DEFAULT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item ALTER COLUMN id SET DEFAULT nextval('public.item_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wishlist id; Type: DEFAULT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.wishlist ALTER COLUMN id SET DEFAULT nextval('public.wishlist_id_seq'::regclass);


--
-- Data for Name: degree_of_desire; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.degree_of_desire (item_id, degree) FROM stdin;
\.


--
-- Data for Name: friend_requests; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.friend_requests (user_id_from, user_id_to) FROM stdin;
\.


--
-- Data for Name: friendship; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.friendship (user_id_1, user_id_2) FROM stdin;
\.


--
-- Data for Name: group; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public."group" (id, title, about, date) FROM stdin;
\.


--
-- Data for Name: group_list; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.group_list (group_id, list_id) FROM stdin;
\.


--
-- Data for Name: group_user; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.group_user (group_id, user_id, role_in_group) FROM stdin;
\.


--
-- Data for Name: item; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.item (id, title, about, access_level, status, giver_id, date_creation, date_for_status) FROM stdin;
\.


--
-- Data for Name: item_group; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.item_group (group_id, item_id) FROM stdin;
\.


--
-- Data for Name: item_list; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.item_list (list_id, item_id) FROM stdin;
\.


--
-- Data for Name: item_picture; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.item_picture (item_id, path_to_picture) FROM stdin;
\.


--
-- Data for Name: user_item; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.user_item (user_id, item_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.users (id, phone_number, username, surname, userpic, about, birthday, password_hash, nickname, email, token, token_expiration, last_seen) FROM stdin;
1	\N	Dmitry	\N	\N	\N	\N	pbkdf2:sha256:150000$k5ee4ntq$900dadbd9d61d3dbd099bb3da1b49e8affc088650bdd70c3272fb76d97dabd23	johuex	polds@list.ru	\N	\N	2021-03-10 19:21:53.992+00
\.


--
-- Data for Name: wishlist; Type: TABLE DATA; Schema: public; Owner: johuex
--

COPY public.wishlist (id, user_id, title, about, access_level) FROM stdin;
\.


--
-- Name: group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: johuex
--

SELECT pg_catalog.setval('public.group_id_seq', 1, false);


--
-- Name: item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: johuex
--

SELECT pg_catalog.setval('public.item_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: johuex
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: wishlist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: johuex
--

SELECT pg_catalog.setval('public.wishlist_id_seq', 1, false);


--
-- Name: degree_of_desire degree_of_desire_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.degree_of_desire
    ADD CONSTRAINT degree_of_desire_pk PRIMARY KEY (item_id);


--
-- Name: friend_requests friend_requests_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT friend_requests_pk PRIMARY KEY (user_id_from, user_id_to);


--
-- Name: friendship friendship_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friendship
    ADD CONSTRAINT friendship_pk PRIMARY KEY (user_id_1, user_id_2);


--
-- Name: group_list group_list_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_list
    ADD CONSTRAINT group_list_pk PRIMARY KEY (group_id, list_id);


--
-- Name: group group_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public."group"
    ADD CONSTRAINT group_pk PRIMARY KEY (id);


--
-- Name: group_user group_user_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_user
    ADD CONSTRAINT group_user_pk PRIMARY KEY (group_id, user_id);


--
-- Name: item_group item_group_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_group
    ADD CONSTRAINT item_group_pk PRIMARY KEY (item_id, group_id);


--
-- Name: item_list item_list_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_list
    ADD CONSTRAINT item_list_pk PRIMARY KEY (list_id, item_id);


--
-- Name: item_picture item_picture_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_picture
    ADD CONSTRAINT item_picture_pk PRIMARY KEY (item_id);


--
-- Name: item item_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_pk PRIMARY KEY (id);


--
-- Name: user_item user_item_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT user_item_pk PRIMARY KEY (user_id, item_id);


--
-- Name: users users_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);


--
-- Name: wishlist wishlist_pk; Type: CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.wishlist
    ADD CONSTRAINT wishlist_pk PRIMARY KEY (id);


--
-- Name: users_email_uindex; Type: INDEX; Schema: public; Owner: johuex
--

CREATE UNIQUE INDEX users_email_uindex ON public.users USING btree (email);


--
-- Name: users_nickname_uindex; Type: INDEX; Schema: public; Owner: johuex
--

CREATE UNIQUE INDEX users_nickname_uindex ON public.users USING btree (nickname);


--
-- Name: users_token_uindex; Type: INDEX; Schema: public; Owner: johuex
--

CREATE UNIQUE INDEX users_token_uindex ON public.users USING btree (token);


--
-- Name: degree_of_desire degree_of_desire_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.degree_of_desire
    ADD CONSTRAINT degree_of_desire_item_id_fk FOREIGN KEY (item_id) REFERENCES public.item(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: friend_requests friend_requests_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT friend_requests_users_id_fk FOREIGN KEY (user_id_from) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: friend_requests friend_requests_users_id_fk_2; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friend_requests
    ADD CONSTRAINT friend_requests_users_id_fk_2 FOREIGN KEY (user_id_to) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: friendship friendship_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friendship
    ADD CONSTRAINT friendship_users_id_fk FOREIGN KEY (user_id_1) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: friendship friendship_users_id_fk_2; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.friendship
    ADD CONSTRAINT friendship_users_id_fk_2 FOREIGN KEY (user_id_2) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: group_list group_list_group_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_list
    ADD CONSTRAINT group_list_group_id_fk FOREIGN KEY (group_id) REFERENCES public."group"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: group_list group_list_wishlist_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_list
    ADD CONSTRAINT group_list_wishlist_id_fk FOREIGN KEY (list_id) REFERENCES public.wishlist(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: group_user group_user_group_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_user
    ADD CONSTRAINT group_user_group_id_fk FOREIGN KEY (group_id) REFERENCES public."group"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: group_user group_user_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.group_user
    ADD CONSTRAINT group_user_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item_group item_group_group_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_group
    ADD CONSTRAINT item_group_group_id_fk FOREIGN KEY (group_id) REFERENCES public."group"(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item_group item_group_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_group
    ADD CONSTRAINT item_group_item_id_fk FOREIGN KEY (item_id) REFERENCES public.item(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item_list item_list_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_list
    ADD CONSTRAINT item_list_item_id_fk FOREIGN KEY (item_id) REFERENCES public.item(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item_list item_list_wishlist_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_list
    ADD CONSTRAINT item_list_wishlist_id_fk FOREIGN KEY (list_id) REFERENCES public.wishlist(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item_picture item_picture_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item_picture
    ADD CONSTRAINT item_picture_item_id_fk FOREIGN KEY (item_id) REFERENCES public.item(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: item item_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_users_id_fk FOREIGN KEY (giver_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_item user_item_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT user_item_item_id_fk FOREIGN KEY (item_id) REFERENCES public.item(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_item user_item_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.user_item
    ADD CONSTRAINT user_item_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: wishlist wishlist_users_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: johuex
--

ALTER TABLE ONLY public.wishlist
    ADD CONSTRAINT wishlist_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM rdsadmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;
GRANT ALL ON SCHEMA public TO johuex;


--
-- PostgreSQL database dump complete
--

