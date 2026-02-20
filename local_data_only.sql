--
-- PostgreSQL database dump
--

\restrict M0BdozK2aG5K8JWQMySNEPHxcC13fRZIzLRaidgOg7Ryf6Ef2jAVuaCJU826V5o

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

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
-- Data for Name: accounts_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, date_joined, role, admission_number, phone_number, address, emergency_contact, emergency_phone, is_active, is_approved, profile_picture, created_at, updated_at, student_class_id) FROM stdin;
2	pbkdf2_sha256$1200000$JVF3Ob7jyZ8TnojOYQLbyj$K4j/oz6ve1bxlpceZdsGwLXQwuyD3ruyx4/rUx2sPcM=	2026-02-05 15:15:44.921+01	t	admin			admin@school.com	t	2026-01-31 15:52:47+01	ADMIN	TBS/STF/2026/XWYAR	08022566144	No15 Ososami road, Oke Ado Ibadn	Oladimeji Idrees Ademola	08022566144	t	t	user_profiles/teacher-4_NCaKLtK.jpg	2026-01-31 15:52:47.768+01	2026-02-05 15:16:28.727+01	\N
5	pbkdf2_sha256$1200000$PFTK81q8rt8gWo6Y26jbeL$is4wOSr/GoNdnGmH2paMXeiaXIntAdq375kI/flf7x8=	2026-02-10 21:25:58+01	f	teacher3	Idrees	Oladimeji	teacher3@school.com	f	2026-01-31 15:52:54+01	TEACHER	TBS/STF/2026/VCGYF	08022566144	No15 Ososami road, Oke Ado Ibadn			t	t	user_profiles/default_profile.png	2026-01-31 15:52:54.351+01	2026-02-10 21:26:03.195+01	9
9	pbkdf2_sha256$1200000$eAeHZ0Vq47BuHiax1yEZOB$QIYvxj2uipirUqHLVrZnErorDnhN6vhUP8Zi+XA+Vt8=	\N	f	parent4			parent4@mail.com	f	2026-01-31 15:53:02.199+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:02.201+01	2026-01-31 15:53:03.913+01	\N
10	pbkdf2_sha256$1200000$D6ueNvGF9fgt10603zzq9q$daEDItvDOnQ5ZfkOJNDO5KeQD/g/+NkE5kzFSV8V5NE=	\N	f	parent5			parent5@mail.com	f	2026-01-31 15:53:03.93+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:03.931+01	2026-01-31 15:53:05.808+01	\N
11	pbkdf2_sha256$1200000$D131tLEJHH3xXqqOQMNyya$PvLHmr9xa8WFY/zPcYll23X/Pa6hQTLBpQgok16Z6xc=	\N	f	student1			student1@school.com	f	2026-01-31 15:53:05.828+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:05.828+01	2026-01-31 15:53:07.518+01	1
12	pbkdf2_sha256$1200000$w4UaZ9H6L3nuHVWRQ6jdJA$eumYOmknwFA5lP4Xsj4J+nVnFDI8q51uSPRRT00vAf8=	2026-02-01 18:16:15.385+01	f	bola			student2@school.com	f	2026-01-31 15:53:07+01	STUDENT	TBS/2026/3UJCW	07447822446	66 Maidstone	Harley Barnes		t	t	user_profiles/default_profile.png	2026-01-31 15:53:07.555+01	2026-02-01 17:40:04.434+01	2
13	pbkdf2_sha256$1200000$2c8xhMK2viH9i8RJdPvFTW$MddYPL1HcxriW0gJltp31AeNbt5bzJObno3dWe7y7xI=	\N	f	student3			student3@school.com	f	2026-01-31 15:53:09.42+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:09.422+01	2026-01-31 15:53:11.345+01	3
14	pbkdf2_sha256$1200000$20MCN6thrkfCHEGxUCeMEP$lSNhiIXzjONFSFCM8fA/UoYwqjZ61Tl3I4sMTuHOv4c=	\N	f	student4			student4@school.com	f	2026-01-31 15:53:11.382+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:11.383+01	2026-01-31 15:53:13.129+01	4
15	pbkdf2_sha256$1200000$K2PDinl5qqmFg1IqqPlKtf$apqJb2iNpJ1zp8tCHyoNVFl/gLmj1GG19YoY1yRZnE0=	\N	f	student5			student5@school.com	f	2026-01-31 15:53:13.163+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:13.165+01	2026-01-31 15:53:14.946+01	5
16	pbkdf2_sha256$1200000$MkINrtPg2cWfROz4ARypGG$yZo1RpGwypoLQPX/9OqUagW1hx6gEc7mdHB7Wv548YQ=	\N	f	student6			student6@school.com	f	2026-01-31 15:53:14.981+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:14.982+01	2026-01-31 15:53:17.062+01	6
17	pbkdf2_sha256$1200000$rRIrzlu0EyfZOIrq4WBG49$CKSDOCb87/9dIZ4t7XMGBHllprJcFfhM0LjPArYKlfI=	\N	f	student7			student7@school.com	f	2026-01-31 15:53:17.096+01	PARENT	\N	\N	\N			t	t	user_profiles/default_profile.png	2026-01-31 15:53:17.097+01	2026-01-31 15:53:18.883+01	1
18	pbkdf2_sha256$1200000$AxJJlkN8LH3M7WLN6a9Nll$bLj+O1KDDI7gim4R7PrxkBKF532Ec3CsCzJsxWkL88A=	2026-02-01 17:06:52+01	f	sola	Harley	Barnes	student8@school.com	f	2026-01-31 15:53:18+01	STUDENT	TBS/2026/GVOIL	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-01-31 15:53:18.919+01	2026-02-10 21:27:15.589+01	3
19	pbkdf2_sha256$1200000$LZJxyzG17etdXfZcY1jJC3$wxxH9OiH+fRRIUBMf5AnjJsTdbN+UxXQtp1g2sr27/Q=	2026-01-31 16:02:02+01	f	student9	Oladimeji	Ademola	student9@school.com	f	2026-01-31 15:53:20+01	STUDENT	TBS/2026/QPIMA	08022566144	No15 Ososami road, Oke Ado Ibadn			t	t	user_profiles/default_profile.png	2026-01-31 15:53:20.65+01	2026-01-31 16:02:05.117+01	1
21	pbkdf2_sha256$1200000$VO8UHj7ZQlppYrj5CjqHmC$MhO3PojVDkRIcu1i61SxToxyVO9qR1U5flOiIdwdgvU=	2026-02-04 06:09:37.633+01	f	tola	Oladimeji	Ademola	logiclanesolutions@gmail.com	f	2026-02-01 14:43:29+01	STUDENT	TBS/2026/AVMAC	08022566144	No15 Ososami road, Oke Ado Ibadn			t	t	user_profiles/default_profile.png	2026-02-01 14:43:33.012+01	2026-02-01 16:02:51.862+01	3
23	pbkdf2_sha256$1200000$3FX2nL4etJvR6ZNeNnyELB$d9A9mQzo3e02mQciChBL+kJRhPMQRdhfzz91K7nXeHM=	2026-02-12 03:42:07.516+01	f	jane	Harley	Barnes	logiclanesolutions@gmail.com	f	2026-02-01 16:00:43+01	STUDENT	TBS/2026/ZRIQQ	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-02-01 16:00:46.652+01	2026-02-04 17:58:58.806+01	2
3	pbkdf2_sha256$1200000$HxM5nifR5MAosWv6pbsAva$HC7fxpqatqo310LD5eji+Hzq8tASKFhgxRMzEYAWOR0=	2026-02-14 07:14:35.284689+01	f	teacher1	Oladimeji	Ademola	teacher1@school.com	f	2026-01-31 15:52:50+01	TEACHER	TBS/STF/2026/LTQJQ	08022566144	No15 Ososami road, Oke Ado Ibadn			t	t	user_profiles/default_profile.png	2026-01-31 15:52:50.205+01	2026-01-31 15:57:40.414+01	1
20	pbkdf2_sha256$1200000$QEN44pzO1nSZMfSkCozYzU$6nlGwgVJ9VxDw+/aQNqPEjnEdmOZNOGwaG4FaZEVc5k=	2026-02-19 12:38:58.008844+01	f	student10	Harley	Barnes	student10@school.com	f	2026-01-31 15:53:22+01	STUDENT	TBS/2026/WGUFY	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-01-31 15:53:22.567+01	2026-01-31 16:20:55.179+01	1
4	pbkdf2_sha256$1200000$Zpr3ZZXhjbvFgfZB4TGqxu$6TE3iHmMtvl8Anh5GUNm0GH9HHQvT0MLhm37qNO5Uf0=	2026-02-14 21:59:13.933039+01	f	teacher2	Harley	Barnes	teacher2@school.com	f	2026-01-31 15:52:51+01	TEACHER	TBS/STF/2026/XFK3W	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-01-31 15:52:51.988+01	2026-02-10 21:24:28.223+01	12
1	pbkdf2_sha256$1200000$1DQSzXgX0SmYHV2rH4OxPT$bDF/HvKixfi+6aH9/frIw77MGDssAy4LF0HBsqAQwhU=	2026-02-19 12:50:35.605959+01	t	idrees	Oladimeji	Ademola	logiclanesolutions@gmail.com	t	2026-01-31 14:00:29+01	ADMIN	TBS/STF/2026/LJQ9J	08022566144	No15 Ososami road, Oke Ado Ibadn	Oladimeji Idrees Ademola	08022566144	t	t	user_profiles/icon-1.png	2026-01-31 14:00:31.225+01	2026-01-31 15:54:45.393+01	\N
6	pbkdf2_sha256$1200000$im4T8tAoUbIEZiioLSWgys$jReCDtGOmUcMMxBLjG31+FwbIkdpP0wtUHzrHxxgquo=	2026-02-19 12:47:45.079872+01	f	baba	Harley	Barnes	parent1@mail.com	f	2026-01-31 15:52:56+01	PARENT	\N	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-01-31 15:52:56.417+01	2026-02-11 05:54:11.265+01	\N
7	pbkdf2_sha256$1200000$8vSFp002opKHNzHCmpebL7$SgoHin2ZgAjsIQQ0jXkNNp27QuWMf6lr/a/23H8exBs=	2026-02-19 12:49:49.026682+01	f	parent2			parent2@mail.com	f	2026-01-31 15:52:58.288+01	PARENT	\N	08022566144	No15 Ososami road, Oke Ado Ibadn	Oladimeji Idrees Ademola	07447822446	t	t	user_profiles/background.png	2026-01-31 15:52:58.288+01	2026-02-04 18:04:02.123+01	\N
8	pbkdf2_sha256$1200000$4v0bUbT1Y35M4A3cukmHjR$CYHIsf9fXcHDhusMKijsbMgueb4TCW3pPsneROllH5c=	2026-02-19 12:51:37.194766+01	f	parent3			parent3@mail.com	f	2026-01-31 15:53:00.174+01	PARENT	\N	07447822446	66 Maidstone	Harley Barnes	08022566144	t	t	user_profiles/hero-bg_DdnIOwl.jpg	2026-01-31 15:53:00.176+01	2026-02-19 12:52:07.271576+01	\N
22	pbkdf2_sha256$1200000$x7WpVzP1C1tQruWVPX8FW3$aBhBROjmnhxaCDa9LlQZobwfZmIKlepn+GdT7uFC3xk=	2026-02-19 12:44:37.672177+01	f	jade	Oladimeji	Ademola	logiclanesolutions@gmail.com	f	2026-02-01 14:55:47+01	STUDENT	TBS/2026/IPL9K	07447822446	66 Maidstone			t	t	user_profiles/default_profile.png	2026-02-01 14:55:51.373+01	2026-02-01 16:03:45.986+01	3
\.


--
-- Data for Name: accounts_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_student (user_ptr_id) FROM stdin;
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: accounts_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: accounts_user_parents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_user_parents (id, from_user_id, to_user_id) FROM stdin;
1	11	6
2	12	7
3	13	8
4	14	9
5	15	10
6	16	6
7	17	7
8	18	8
9	18	6
10	19	9
11	19	6
12	19	7
13	20	6
14	20	7
15	21	8
16	22	8
17	23	6
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	contenttypes	contenttype
5	sessions	session
6	exams	broadcast
7	exams	chatmessage
8	exams	choice
9	exams	exam
10	exams	examaccess
11	exams	examattempt
12	exams	notification
13	exams	ptarequest
14	exams	question
15	exams	retakerequest
16	exams	schoolclass
17	exams	studentanswer
18	exams	subject
19	exams	subjectivemark
20	exams	systemlog
21	accounts	parent
22	accounts	student
23	accounts	teacher
24	accounts	user
25	brillspay	brillspaylog
26	brillspay	cart
27	brillspay	cartitem
28	brillspay	order
29	brillspay	orderitem
30	brillspay	paymenttransaction
31	brillspay	product
32	brillspay	productcategory
33	brillspay	transaction
34	pickup	pickupauthorization
35	pickup	pickupstudent
36	pickup	pickupverificationlog
37	payroll	auditlog
38	payroll	bankaccount
39	payroll	payee
40	payroll	payeesalarystructure
41	payroll	paymentbatch
42	payroll	paymenttransaction
43	payroll	payrolllineitem
44	payroll	payrollperiod
45	payroll	payrollrecord
46	payroll	salarycomponent
47	payroll	salarystructure
48	payroll	salarystructureitem
49	payroll	schoolsettings
50	loans	loanapplication
51	loans	loanrepayment
52	leaves	leaverequest
53	leaves	leavetype
54	dashboards	attempthistory
55	dashboards	bulkexportjob
56	dashboards	bulkimportjob
57	dashboards	certificate
58	dashboards	certificatetemplate
59	dashboards	chatroom
60	dashboards	chatroommessage
61	dashboards	chatroomreadstatus
62	dashboards	examanalytics
63	dashboards	examschedule
64	dashboards	gradingrubric
65	dashboards	notification
66	dashboards	permission
67	dashboards	questionbank
68	dashboards	questioncategory
69	dashboards	questionchoice
70	dashboards	questiontag
71	dashboards	role
72	dashboards	rolepermission
73	dashboards	rubriccriteria
74	dashboards	rubriccriteriagrade
75	dashboards	rubricgrade
76	dashboards	rubricscore
77	dashboards	schedulednotification
78	dashboards	studentperformance
79	dashboards	userrole
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
317	Can add permission	66	add_permission
318	Can change permission	66	change_permission
319	Can delete permission	66	delete_permission
320	Can view permission	66	view_permission
321	Can add question tag	70	add_questiontag
322	Can change question tag	70	change_questiontag
323	Can delete question tag	70	delete_questiontag
324	Can view question tag	70	view_questiontag
325	Can add exam analytics	62	add_examanalytics
326	Can change exam analytics	62	change_examanalytics
327	Can delete exam analytics	62	delete_examanalytics
328	Can view exam analytics	62	view_examanalytics
329	Can add exam schedule	63	add_examschedule
330	Can change exam schedule	63	change_examschedule
331	Can delete exam schedule	63	delete_examschedule
332	Can view exam schedule	63	view_examschedule
333	Can add grading rubric	64	add_gradingrubric
334	Can change grading rubric	64	change_gradingrubric
335	Can delete grading rubric	64	delete_gradingrubric
336	Can view grading rubric	64	view_gradingrubric
337	Can add question category	68	add_questioncategory
338	Can change question category	68	change_questioncategory
339	Can delete question category	68	delete_questioncategory
340	Can view question category	68	view_questioncategory
341	Can add question bank	67	add_questionbank
342	Can change question bank	67	change_questionbank
343	Can delete question bank	67	delete_questionbank
344	Can view question bank	67	view_questionbank
345	Can add question choice	69	add_questionchoice
346	Can change question choice	69	change_questionchoice
347	Can delete question choice	69	delete_questionchoice
348	Can view question choice	69	view_questionchoice
349	Can add role	71	add_role
350	Can change role	71	change_role
351	Can delete role	71	delete_role
352	Can view role	71	view_role
353	Can add role permission	72	add_rolepermission
354	Can change role permission	72	change_rolepermission
355	Can delete role permission	72	delete_rolepermission
356	Can view role permission	72	view_rolepermission
357	Can add rubric criteria	73	add_rubriccriteria
358	Can change rubric criteria	73	change_rubriccriteria
359	Can delete rubric criteria	73	delete_rubriccriteria
360	Can view rubric criteria	73	view_rubriccriteria
361	Can add rubric grade	75	add_rubricgrade
362	Can change rubric grade	75	change_rubricgrade
363	Can delete rubric grade	75	delete_rubricgrade
364	Can view rubric grade	75	view_rubricgrade
365	Can add rubric score	76	add_rubricscore
366	Can change rubric score	76	change_rubricscore
367	Can delete rubric score	76	delete_rubricscore
368	Can view rubric score	76	view_rubricscore
369	Can add rubric criteria grade	74	add_rubriccriteriagrade
370	Can change rubric criteria grade	74	change_rubriccriteriagrade
371	Can delete rubric criteria grade	74	delete_rubriccriteriagrade
372	Can view rubric criteria grade	74	view_rubriccriteriagrade
373	Can add scheduled notification	77	add_schedulednotification
374	Can change scheduled notification	77	change_schedulednotification
375	Can delete scheduled notification	77	delete_schedulednotification
376	Can view scheduled notification	77	view_schedulednotification
377	Can add student performance	78	add_studentperformance
378	Can change student performance	78	change_studentperformance
379	Can delete student performance	78	delete_studentperformance
380	Can view student performance	78	view_studentperformance
381	Can add user role	79	add_userrole
382	Can change user role	79	change_userrole
383	Can delete user role	79	delete_userrole
384	Can view user role	79	view_userrole
385	Can add notification	65	add_notification
386	Can change notification	65	change_notification
387	Can delete notification	65	delete_notification
388	Can view notification	65	view_notification
389	Can add chat room	59	add_chatroom
390	Can change chat room	59	change_chatroom
391	Can delete chat room	59	delete_chatroom
392	Can view chat room	59	view_chatroom
393	Can add chat room message	60	add_chatroommessage
394	Can change chat room message	60	change_chatroommessage
395	Can delete chat room message	60	delete_chatroommessage
396	Can view chat room message	60	view_chatroommessage
397	Can add chat room read status	61	add_chatroomreadstatus
398	Can change chat room read status	61	change_chatroomreadstatus
399	Can delete chat room read status	61	delete_chatroomreadstatus
400	Can view chat room read status	61	view_chatroomreadstatus
257	Can add role	68	add_role
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add system log	20	add_systemlog
22	Can change system log	20	change_systemlog
23	Can delete system log	20	delete_systemlog
24	Can view system log	20	view_systemlog
25	Can add chat message	7	add_chatmessage
26	Can change chat message	7	change_chatmessage
27	Can delete chat message	7	delete_chatmessage
28	Can view chat message	7	view_chatmessage
29	Can add exam	9	add_exam
30	Can change exam	9	change_exam
31	Can delete exam	9	delete_exam
32	Can view exam	9	view_exam
33	Can add exam attempt	11	add_examattempt
34	Can change exam attempt	11	change_examattempt
35	Can delete exam attempt	11	delete_examattempt
36	Can view exam attempt	11	view_examattempt
37	Can add notification	12	add_notification
38	Can change notification	12	change_notification
39	Can delete notification	12	delete_notification
40	Can view notification	12	view_notification
41	Can add pta request	13	add_ptarequest
42	Can change pta request	13	change_ptarequest
43	Can delete pta request	13	delete_ptarequest
44	Can view pta request	13	view_ptarequest
45	Can add question	14	add_question
46	Can change question	14	change_question
47	Can delete question	14	delete_question
48	Can view question	14	view_question
49	Can add choice	8	add_choice
50	Can change choice	8	change_choice
51	Can delete choice	8	delete_choice
52	Can view choice	8	view_choice
53	Can add retake request	15	add_retakerequest
54	Can change retake request	15	change_retakerequest
55	Can delete retake request	15	delete_retakerequest
56	Can view retake request	15	view_retakerequest
57	Can add school class	16	add_schoolclass
58	Can change school class	16	change_schoolclass
59	Can delete school class	16	delete_schoolclass
60	Can view school class	16	view_schoolclass
61	Can add broadcast	6	add_broadcast
62	Can change broadcast	6	change_broadcast
63	Can delete broadcast	6	delete_broadcast
64	Can view broadcast	6	view_broadcast
65	Can add student answer	17	add_studentanswer
66	Can change student answer	17	change_studentanswer
67	Can delete student answer	17	delete_studentanswer
68	Can view student answer	17	view_studentanswer
69	Can add subject	18	add_subject
70	Can change subject	18	change_subject
71	Can delete subject	18	delete_subject
72	Can view subject	18	view_subject
73	Can add subjective mark	19	add_subjectivemark
74	Can change subjective mark	19	change_subjectivemark
75	Can delete subjective mark	19	delete_subjectivemark
76	Can view subjective mark	19	view_subjectivemark
77	Can add exam access	10	add_examaccess
78	Can change exam access	10	change_examaccess
79	Can delete exam access	10	delete_examaccess
80	Can view exam access	10	view_examaccess
81	Can add user	24	add_user
82	Can change user	24	change_user
83	Can delete user	24	delete_user
84	Can view user	24	view_user
85	Can add Student	22	add_student
86	Can change Student	22	change_student
87	Can delete Student	22	delete_student
88	Can view Student	22	view_student
89	Can add Parent/Guardian	21	add_parent
90	Can change Parent/Guardian	21	change_parent
91	Can delete Parent/Guardian	21	delete_parent
92	Can view Parent/Guardian	21	view_parent
93	Can add Staff Member	23	add_teacher
94	Can change Staff Member	23	change_teacher
95	Can delete Staff Member	23	delete_teacher
96	Can view Staff Member	23	view_teacher
97	Can add product category	32	add_productcategory
98	Can change product category	32	change_productcategory
99	Can delete product category	32	delete_productcategory
100	Can view product category	32	view_productcategory
101	Can add cart	26	add_cart
102	Can change cart	26	change_cart
103	Can delete cart	26	delete_cart
104	Can view cart	26	view_cart
105	Can add order	28	add_order
106	Can change order	28	change_order
107	Can delete order	28	delete_order
108	Can view order	28	view_order
109	Can add brills pay log	25	add_brillspaylog
110	Can change brills pay log	25	change_brillspaylog
111	Can delete brills pay log	25	delete_brillspaylog
112	Can view brills pay log	25	view_brillspaylog
113	Can add order item	29	add_orderitem
114	Can change order item	29	change_orderitem
115	Can delete order item	29	delete_orderitem
116	Can view order item	29	view_orderitem
117	Can add payment transaction	30	add_paymenttransaction
118	Can change payment transaction	30	change_paymenttransaction
119	Can delete payment transaction	30	delete_paymenttransaction
120	Can view payment transaction	30	view_paymenttransaction
121	Can add product	31	add_product
122	Can change product	31	change_product
123	Can delete product	31	delete_product
124	Can view product	31	view_product
125	Can add transaction	33	add_transaction
126	Can change transaction	33	change_transaction
127	Can delete transaction	33	delete_transaction
128	Can view transaction	33	view_transaction
129	Can add cart item	27	add_cartitem
130	Can change cart item	27	change_cartitem
131	Can delete cart item	27	delete_cartitem
132	Can view cart item	27	view_cartitem
133	Can add pickup authorization	34	add_pickupauthorization
134	Can change pickup authorization	34	change_pickupauthorization
135	Can delete pickup authorization	34	delete_pickupauthorization
136	Can view pickup authorization	34	view_pickupauthorization
137	Can add pickup student	35	add_pickupstudent
138	Can change pickup student	35	change_pickupstudent
139	Can delete pickup student	35	delete_pickupstudent
140	Can view pickup student	35	view_pickupstudent
141	Can add pickup verification log	36	add_pickupverificationlog
142	Can change pickup verification log	36	change_pickupverificationlog
143	Can delete pickup verification log	36	delete_pickupverificationlog
144	Can view pickup verification log	36	view_pickupverificationlog
145	Can add salary component	46	add_salarycomponent
146	Can change salary component	46	change_salarycomponent
147	Can delete salary component	46	delete_salarycomponent
148	Can view salary component	46	view_salarycomponent
149	Can add salary structure	47	add_salarystructure
150	Can change salary structure	47	change_salarystructure
151	Can delete salary structure	47	delete_salarystructure
152	Can view salary structure	47	view_salarystructure
153	Can add school settings	49	add_schoolsettings
154	Can change school settings	49	change_schoolsettings
155	Can delete school settings	49	delete_schoolsettings
156	Can view school settings	49	view_schoolsettings
157	Can add audit log	37	add_auditlog
158	Can change audit log	37	change_auditlog
159	Can delete audit log	37	delete_auditlog
160	Can view audit log	37	view_auditlog
161	Can add payee	39	add_payee
162	Can change payee	39	change_payee
163	Can delete payee	39	delete_payee
164	Can view payee	39	view_payee
165	Can add payroll period	44	add_payrollperiod
166	Can change payroll period	44	change_payrollperiod
167	Can delete payroll period	44	delete_payrollperiod
168	Can view payroll period	44	view_payrollperiod
169	Can add payment batch	41	add_paymentbatch
170	Can change payment batch	41	change_paymentbatch
171	Can delete payment batch	41	delete_paymentbatch
172	Can view payment batch	41	view_paymentbatch
173	Can add payroll record	45	add_payrollrecord
174	Can change payroll record	45	change_payrollrecord
175	Can delete payroll record	45	delete_payrollrecord
176	Can view payroll record	45	view_payrollrecord
177	Can add payroll line item	43	add_payrolllineitem
178	Can change payroll line item	43	change_payrolllineitem
179	Can delete payroll line item	43	delete_payrolllineitem
180	Can view payroll line item	43	view_payrolllineitem
181	Can add payment transaction	42	add_paymenttransaction
182	Can change payment transaction	42	change_paymenttransaction
183	Can delete payment transaction	42	delete_paymenttransaction
184	Can view payment transaction	42	view_paymenttransaction
185	Can add payee salary structure	40	add_payeesalarystructure
186	Can change payee salary structure	40	change_payeesalarystructure
187	Can delete payee salary structure	40	delete_payeesalarystructure
188	Can view payee salary structure	40	view_payeesalarystructure
189	Can add salary structure item	48	add_salarystructureitem
190	Can change salary structure item	48	change_salarystructureitem
191	Can delete salary structure item	48	delete_salarystructureitem
192	Can view salary structure item	48	view_salarystructureitem
193	Can add bank account	38	add_bankaccount
194	Can change bank account	38	change_bankaccount
195	Can delete bank account	38	delete_bankaccount
196	Can view bank account	38	view_bankaccount
197	Can add loan application	50	add_loanapplication
198	Can change loan application	50	change_loanapplication
199	Can delete loan application	50	delete_loanapplication
200	Can view loan application	50	view_loanapplication
201	Can add loan repayment	51	add_loanrepayment
202	Can change loan repayment	51	change_loanrepayment
203	Can delete loan repayment	51	delete_loanrepayment
204	Can view loan repayment	51	view_loanrepayment
205	Can add leave type	53	add_leavetype
206	Can change leave type	53	change_leavetype
207	Can delete leave type	53	delete_leavetype
208	Can view leave type	53	view_leavetype
209	Can add leave request	52	add_leaverequest
210	Can change leave request	52	change_leaverequest
211	Can delete leave request	52	delete_leaverequest
212	Can view leave request	52	view_leaverequest
213	Can add permission	63	add_permission
214	Can change permission	63	change_permission
215	Can delete permission	63	delete_permission
216	Can view permission	63	view_permission
217	Can add question tag	67	add_questiontag
218	Can change question tag	67	change_questiontag
219	Can delete question tag	67	delete_questiontag
220	Can view question tag	67	view_questiontag
221	Can add bulk export job	55	add_bulkexportjob
222	Can change bulk export job	55	change_bulkexportjob
223	Can delete bulk export job	55	delete_bulkexportjob
224	Can view bulk export job	55	view_bulkexportjob
225	Can add bulk import job	56	add_bulkimportjob
226	Can change bulk import job	56	change_bulkimportjob
227	Can delete bulk import job	56	delete_bulkimportjob
228	Can view bulk import job	56	view_bulkimportjob
229	Can add certificate template	58	add_certificatetemplate
230	Can change certificate template	58	change_certificatetemplate
231	Can delete certificate template	58	delete_certificatetemplate
232	Can view certificate template	58	view_certificatetemplate
233	Can add exam analytics	59	add_examanalytics
234	Can change exam analytics	59	change_examanalytics
235	Can delete exam analytics	59	delete_examanalytics
236	Can view exam analytics	59	view_examanalytics
237	Can add exam schedule	60	add_examschedule
238	Can change exam schedule	60	change_examschedule
239	Can delete exam schedule	60	delete_examschedule
240	Can view exam schedule	60	view_examschedule
241	Can add grading rubric	61	add_gradingrubric
242	Can change grading rubric	61	change_gradingrubric
243	Can delete grading rubric	61	delete_gradingrubric
244	Can view grading rubric	61	view_gradingrubric
245	Can add question category	65	add_questioncategory
246	Can change question category	65	change_questioncategory
247	Can delete question category	65	delete_questioncategory
248	Can view question category	65	view_questioncategory
249	Can add question bank	64	add_questionbank
250	Can change question bank	64	change_questionbank
251	Can delete question bank	64	delete_questionbank
252	Can view question bank	64	view_questionbank
253	Can add question choice	66	add_questionchoice
254	Can change question choice	66	change_questionchoice
255	Can delete question choice	66	delete_questionchoice
256	Can view question choice	66	view_questionchoice
258	Can change role	68	change_role
259	Can delete role	68	delete_role
260	Can view role	68	view_role
261	Can add role permission	69	add_rolepermission
262	Can change role permission	69	change_rolepermission
263	Can delete role permission	69	delete_rolepermission
264	Can view role permission	69	view_rolepermission
265	Can add rubric criteria	70	add_rubriccriteria
266	Can change rubric criteria	70	change_rubriccriteria
267	Can delete rubric criteria	70	delete_rubriccriteria
268	Can view rubric criteria	70	view_rubriccriteria
269	Can add rubric grade	72	add_rubricgrade
270	Can change rubric grade	72	change_rubricgrade
271	Can delete rubric grade	72	delete_rubricgrade
272	Can view rubric grade	72	view_rubricgrade
273	Can add rubric score	73	add_rubricscore
274	Can change rubric score	73	change_rubricscore
275	Can delete rubric score	73	delete_rubricscore
276	Can view rubric score	73	view_rubricscore
277	Can add rubric criteria grade	71	add_rubriccriteriagrade
278	Can change rubric criteria grade	71	change_rubriccriteriagrade
279	Can delete rubric criteria grade	71	delete_rubriccriteriagrade
280	Can view rubric criteria grade	71	view_rubriccriteriagrade
281	Can add scheduled notification	74	add_schedulednotification
282	Can change scheduled notification	74	change_schedulednotification
283	Can delete scheduled notification	74	delete_schedulednotification
284	Can view scheduled notification	74	view_schedulednotification
285	Can add student performance	75	add_studentperformance
286	Can change student performance	75	change_studentperformance
287	Can delete student performance	75	delete_studentperformance
288	Can view student performance	75	view_studentperformance
289	Can add user role	76	add_userrole
290	Can change user role	76	change_userrole
291	Can delete user role	76	delete_userrole
292	Can view user role	76	view_userrole
293	Can add attempt history	54	add_attempthistory
294	Can change attempt history	54	change_attempthistory
295	Can delete attempt history	54	delete_attempthistory
296	Can view attempt history	54	view_attempthistory
297	Can add certificate	57	add_certificate
298	Can change certificate	57	change_certificate
299	Can delete certificate	57	delete_certificate
300	Can view certificate	57	view_certificate
301	Can add notification	62	add_notification
302	Can change notification	62	change_notification
303	Can delete notification	62	delete_notification
304	Can view notification	62	view_notification
305	Can add chat room	77	add_chatroom
306	Can change chat room	77	change_chatroom
307	Can delete chat room	77	delete_chatroom
308	Can view chat room	77	view_chatroom
309	Can add chat room message	78	add_chatroommessage
310	Can change chat room message	78	change_chatroommessage
311	Can delete chat room message	78	delete_chatroommessage
312	Can view chat room message	78	view_chatroommessage
313	Can add chat room read status	79	add_chatroomreadstatus
314	Can change chat room read status	79	change_chatroomreadstatus
315	Can delete chat room read status	79	delete_chatroomreadstatus
316	Can view chat room read status	79	view_chatroomreadstatus
\.


--
-- Data for Name: accounts_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: exams_schoolclass; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_schoolclass (id, name, level, academic_year, description, is_active, created_at, assistant_teacher_id, teacher_id) FROM stdin;
1	JSS1	junior_secondary	2025/2026		t	2026-01-31 15:52:47.594+01	3	3
2	JSS2	Kindergarten			t	2026-01-31 15:52:47.612+01	\N	\N
3	JSS3	Kindergarten			t	2026-01-31 15:52:47.632+01	\N	\N
4	SSS1	Kindergarten			t	2026-01-31 15:52:47.652+01	\N	\N
5	SSS2	Kindergarten			t	2026-01-31 15:52:47.669+01	\N	\N
6	SSS3	Kindergarten			t	2026-01-31 15:52:47.687+01	\N	\N
9	PRIMARY 1	primary	2025/2026		t	2026-02-01 12:46:10.606+01	3	3
10	PRIMARY 3	primary	2025/2026		t	2026-02-01 15:03:47.856+01	3	3
11	JSS 1	junior_secondary	2023/2024		t	2026-02-04 02:11:34.594+01	\N	1
12	JSS 2	junior_secondary	2023/2024		t	2026-02-04 02:11:34.611+01	\N	1
13	SSS 1	senior_secondary	2023/2024		t	2026-02-04 02:11:34.63+01	\N	1
14	Primary 1 Verification	Kindergarten			t	2026-02-04 07:51:38.849+01	\N	\N
\.


--
-- Data for Name: exams_exam; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_exam (id, title, duration, start_time, end_time, is_active, created_at, is_published, allow_retake, requires_payment, price, passing_marks, created_by_id, school_class_id) FROM stdin;
47	Computer Science Fundamentals	60	2026-02-04 13:36:03.68+01	2026-03-11 13:36:03.68+01	t	2026-02-09 13:36:03.68+01	t	t	f	0	50	3	11
48	World History: 20th Century	90	2026-02-07 13:36:04.042+01	2026-03-11 13:36:04.042+01	t	2026-02-09 13:36:04.043+01	t	f	f	0	40	3	11
49	Advanced Physics: Mechanics	120	2026-01-30 13:36:04.263+01	2026-03-11 13:36:04.263+01	t	2026-02-09 13:36:04.264+01	t	f	f	0	60	3	11
50	First Term Exam Math	5	2026-02-09 15:49:00+01	2026-02-28 15:49:00+01	t	2026-02-09 15:52:44.323+01	t	t	f	0	40	3	3
\.


--
-- Data for Name: brillspay_order; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_order (id, reference, status, total_amount, is_override, created_at, buyer_id, exam_id, ward_id) FROM stdin;
0a7d0782-5f22-4faa-b0dc-79a211a42fff	BP-97F86FB2F0	PAID	7500.00	f	2026-02-11 06:07:43.467+01	6	\N	23
0cd3564e-4865-4603-a752-a3f26722682d	BP-5168EB0CAC	PAID	2500.00	f	2026-02-11 06:06:43.116+01	6	\N	20
22a85176-2b5d-474c-a954-d5893efc0afd	BP-3CE71FEF80	PENDING	2500.00	f	2026-02-12 04:51:49.621+01	7	\N	12
535bede6-2ef0-463f-8990-b143cb47daba	BP-CC153BC29B	PENDING	7500.00	f	2026-02-12 04:59:12.785+01	7	\N	12
68708e92-4251-426d-9df4-7c5e753016e3	BP-5D071AE458	PENDING	7500.00	f	2026-02-11 06:05:08.626+01	6	\N	20
fe311fae-7137-4893-8e76-13ba123370b2	BP-ABC9A2366A	PENDING	2500.00	f	2026-02-12 04:54:27.465+01	7	\N	12
5219369c-9afd-488f-b7a1-59234760eef7	BP-308D1D6AC0	PENDING	15000.00	f	2026-02-14 07:11:27.71752+01	6	\N	18
\.


--
-- Data for Name: brillspay_brillspaylog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_brillspaylog (id, action, message, metadata, created_at, user_id, order_id) FROM stdin;
1	ORDER_CREATED	Order created from cart	\N	2026-02-11 06:05:08.642+01	6	68708e92-4251-426d-9df4-7c5e753016e3
2	ORDER_CREATED	Order created from cart	\N	2026-02-11 06:06:43.153+01	6	0cd3564e-4865-4603-a752-a3f26722682d
3	PAYMENT_SUCCESS	Paystack payment confirmed via webhook	{"amount": 250000, "gateway_reference": "dcvgb0kkyi"}	2026-02-11 06:06:59.405+01	6	0cd3564e-4865-4603-a752-a3f26722682d
4	ORDER_CREATED	Order created from cart	\N	2026-02-11 06:07:43.483+01	6	0a7d0782-5f22-4faa-b0dc-79a211a42fff
5	PAYMENT_SUCCESS	Paystack payment confirmed via webhook	{"amount": 750000, "gateway_reference": "lo2ke26jmh"}	2026-02-11 06:08:05.112+01	6	0a7d0782-5f22-4faa-b0dc-79a211a42fff
6	ORDER_CREATED	Order created from cart	\N	2026-02-12 04:51:49.656+01	7	22a85176-2b5d-474c-a954-d5893efc0afd
7	ORDER_CREATED	Order created from cart	\N	2026-02-12 04:54:27.48+01	7	fe311fae-7137-4893-8e76-13ba123370b2
8	ORDER_CREATED	Order created from cart	\N	2026-02-12 04:59:12.798+01	7	535bede6-2ef0-463f-8990-b143cb47daba
9	ORDER_CREATED	Order created from cart	\N	2026-02-14 07:11:27.753199+01	6	5219369c-9afd-488f-b7a1-59234760eef7
\.


--
-- Data for Name: brillspay_cart; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_cart (id, created_at, updated_at, user_id, ward_id) FROM stdin;
1	2026-02-11 05:58:00.655+01	2026-02-11 05:58:00.655+01	6	19
4	2026-02-12 04:49:10.631+01	2026-02-12 04:49:10.631+01	7	12
5	2026-02-12 05:10:37.642+01	2026-02-12 05:10:37.642+01	6	20
6	2026-02-13 22:22:35.051388+01	2026-02-13 22:22:35.051388+01	6	18
\.


--
-- Data for Name: brillspay_productcategory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_productcategory (id, class_name, slug, is_active) FROM stdin;
1	JSS1	jss1	t
2	JSS2	jss2	t
3	JSS3	jss3	t
4	SSS1	sss1	t
5	SSS2	sss2	t
6	SSS3	sss3	t
\.


--
-- Data for Name: brillspay_product; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_product (id, name, price, stock_quantity, image, description, is_active, created_at, category_id) FROM stdin;
15b0ff0a-4130-4687-9c24-aec80603b065	JSS1 Result Analytics	2500.00	100	products/chemistry.jpg	Advanced performance analytics for JSS1	t	2026-01-31 15:53:24.327+01	1
2d126965-4431-4640-af2a-1ae122ded8b0	SSS1 CBT Exam Access	5000.00	100		Full CBT exam access for SSS1	t	2026-01-31 15:53:24.34+01	4
331fa274-261d-4634-aceb-e6deb24ea921	SSS1 Result Analytics	2500.00	100		Advanced performance analytics for SSS1	t	2026-01-31 15:53:24.342+01	4
4520ea05-8030-450c-945f-63bd08b69b4e	SSS2 CBT Exam Access	5000.00	100		Full CBT exam access for SSS2	t	2026-01-31 15:53:24.344+01	5
4edabe3f-d4f6-48a9-9147-60fcc1ef721b	SSS2 Result Analytics	2500.00	100		Advanced performance analytics for SSS2	t	2026-01-31 15:53:24.347+01	5
65f43ef6-d311-4d6d-ba5f-f330d89062d5	SSS3 CBT Exam Access	5000.00	100		Full CBT exam access for SSS3	t	2026-01-31 15:53:24.35+01	6
8cffbd22-8ae6-4bab-832d-ab7eabc8bd7d	JSS1 CBT Exam Access	5000.00	100		Full CBT exam access for JSS1	t	2026-01-31 15:53:24.325+01	1
974f2b01-10c9-44da-95e7-290409866c67	JSS2 CBT Exam Access	5000.00	100		Full CBT exam access for JSS2	t	2026-01-31 15:53:24.33+01	2
a5c8a3b5-483f-42d1-8a94-14c4c5ddb45b	JSS3 CBT Exam Access	5000.00	100	products/background.jpg	Full CBT exam access for JSS3	t	2026-01-31 15:53:24.335+01	3
b7617a3a-56f4-4321-80c6-49692ce88c98	JSS2 Result Analytics	2500.00	100	products/cbt.jpg	Advanced performance analytics for JSS2	t	2026-01-31 15:53:24.332+01	2
c765cfbe-48f5-4fbc-b2bc-2dfdff48e02a	JSS3 Result Analytics	2500.00	100		Advanced performance analytics for JSS3	t	2026-01-31 15:53:24.337+01	3
ca7dddf7-7ad8-4de7-b93c-0959771ee7a9	SSS3 Result Analytics	2500.00	100	products/about-school_9L6OEUL.png	Advanced performance analytics for SSS3	t	2026-01-31 15:53:24.351+01	6
\.


--
-- Data for Name: brillspay_cartitem; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_cartitem (id, quantity, cart_id, product_id) FROM stdin;
13	1	1	15b0ff0a-4130-4687-9c24-aec80603b065
\.


--
-- Data for Name: brillspay_orderitem; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_orderitem (id, product_name, price, quantity, order_id, product_id) FROM stdin;
1	JSS1 Result Analytics	2500.00	3	68708e92-4251-426d-9df4-7c5e753016e3	\N
2	JSS1 Result Analytics	2500.00	1	0cd3564e-4865-4603-a752-a3f26722682d	\N
3	JSS2 Result Analytics	2500.00	3	0a7d0782-5f22-4faa-b0dc-79a211a42fff	\N
4	JSS2 Result Analytics	2500.00	1	22a85176-2b5d-474c-a954-d5893efc0afd	\N
5	JSS2 Result Analytics	2500.00	1	fe311fae-7137-4893-8e76-13ba123370b2	b7617a3a-56f4-4321-80c6-49692ce88c98
6	JSS2 CBT Exam Access	5000.00	1	535bede6-2ef0-463f-8990-b143cb47daba	974f2b01-10c9-44da-95e7-290409866c67
7	JSS2 Result Analytics	2500.00	1	535bede6-2ef0-463f-8990-b143cb47daba	b7617a3a-56f4-4321-80c6-49692ce88c98
8	JSS3 CBT Exam Access	5000.00	3	5219369c-9afd-488f-b7a1-59234760eef7	a5c8a3b5-483f-42d1-8a94-14c4c5ddb45b
\.


--
-- Data for Name: brillspay_paymenttransaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_paymenttransaction (id, gateway_reference, gateway_name, amount, verified, raw_response, created_at, order_id) FROM stdin;
1	dcvgb0kkyi	paystack	2500.00	f	{"data": {"reference": "dcvgb0kkyi", "access_code": "vt1z7ar81y7m5wn", "authorization_url": "https://checkout.paystack.com/vt1z7ar81y7m5wn"}, "status": true, "message": "Authorization URL created"}	2026-02-11 06:06:49.945+01	0cd3564e-4865-4603-a752-a3f26722682d
2	lo2ke26jmh	paystack	7500.00	f	{"data": {"reference": "lo2ke26jmh", "access_code": "ply3xs5v8xqszbj", "authorization_url": "https://checkout.paystack.com/ply3xs5v8xqszbj"}, "status": true, "message": "Authorization URL created"}	2026-02-11 06:07:55.918+01	0a7d0782-5f22-4faa-b0dc-79a211a42fff
\.


--
-- Data for Name: brillspay_transaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brillspay_transaction (id, gateway_reference, amount, verified, status, payload, created_at, order_id, user_id, ward_id) FROM stdin;
1	\N	7500.00	f	initialized	\N	2026-02-11 06:05:08.637+01	68708e92-4251-426d-9df4-7c5e753016e3	6	20
2	dcvgb0kkyi	2500.00	t	success	{"data": {"id": 5826983975, "log": null, "fees": 13750, "plan": {}, "split": {}, "amount": 250000, "domain": "test", "paidAt": "2026-02-11T05:06:57.000Z", "source": {"type": "api", "source": "merchant_api", "identifier": null, "entry_point": "transaction_initialize"}, "status": "success", "channel": "card", "message": null, "paid_at": "2026-02-11T05:06:57.000Z", "currency": "NGN", "customer": {"id": 328054401, "email": "parent1@mail.com", "phone": null, "metadata": null, "last_name": null, "first_name": null, "risk_action": "default", "customer_code": "CUS_jx6knybp8b8po8z", "international_format_phone": null}, "metadata": {"user_id": "6", "ward_id": "20", "order_id": "0cd3564e-4865-4603-a752-a3f26722682d", "internal_reference": "BP-5168EB0CAC"}, "order_id": null, "reference": "dcvgb0kkyi", "created_at": "2026-02-11T05:06:48.000Z", "fees_split": null, "ip_address": "197.211.63.30", "subaccount": {}, "authorization": {"bin": "408408", "bank": "TEST BANK", "brand": "visa", "last4": "4081", "channel": "card", "exp_year": "2030", "reusable": true, "card_type": "visa ", "exp_month": "12", "signature": "SIG_p06aSZQRKKPOcssk3FvV", "account_name": null, "country_code": "NG", "receiver_bank": null, "authorization_code": "AUTH_f2y0u1mi8n", "receiver_bank_account_number": null}, "fees_breakdown": null, "gateway_response": "Successful", "requested_amount": 250000, "pos_transaction_data": null}, "event": "charge.success"}	2026-02-11 06:06:43.139+01	0cd3564e-4865-4603-a752-a3f26722682d	6	20
3	lo2ke26jmh	7500.00	t	success	{"data": {"id": 5826986022, "log": null, "fees": 21250, "plan": {}, "split": {}, "amount": 750000, "domain": "test", "paidAt": "2026-02-11T05:08:02.000Z", "source": {"type": "api", "source": "merchant_api", "identifier": null, "entry_point": "transaction_initialize"}, "status": "success", "channel": "card", "message": null, "paid_at": "2026-02-11T05:08:02.000Z", "currency": "NGN", "customer": {"id": 328054401, "email": "parent1@mail.com", "phone": null, "metadata": null, "last_name": null, "first_name": null, "risk_action": "default", "customer_code": "CUS_jx6knybp8b8po8z", "international_format_phone": null}, "metadata": {"user_id": "6", "ward_id": "23", "order_id": "0a7d0782-5f22-4faa-b0dc-79a211a42fff", "internal_reference": "BP-97F86FB2F0"}, "order_id": null, "reference": "lo2ke26jmh", "created_at": "2026-02-11T05:07:54.000Z", "fees_split": null, "ip_address": "197.211.63.30", "subaccount": {}, "authorization": {"bin": "408408", "bank": "TEST BANK", "brand": "visa", "last4": "4081", "channel": "card", "exp_year": "2030", "reusable": true, "card_type": "visa ", "exp_month": "12", "signature": "SIG_p06aSZQRKKPOcssk3FvV", "account_name": null, "country_code": "NG", "receiver_bank": null, "authorization_code": "AUTH_nj9mqvuccz", "receiver_bank_account_number": null}, "fees_breakdown": null, "gateway_response": "Successful", "requested_amount": 750000, "pos_transaction_data": null}, "event": "charge.success"}	2026-02-11 06:07:43.48+01	0a7d0782-5f22-4faa-b0dc-79a211a42fff	6	23
4	\N	2500.00	f	initialized	\N	2026-02-12 04:51:49.65+01	22a85176-2b5d-474c-a954-d5893efc0afd	7	12
5	\N	2500.00	f	initialized	\N	2026-02-12 04:54:27.476+01	fe311fae-7137-4893-8e76-13ba123370b2	7	12
6	\N	7500.00	f	initialized	\N	2026-02-12 04:59:12.797+01	535bede6-2ef0-463f-8990-b143cb47daba	7	12
7	\N	15000.00	f	initialized	\N	2026-02-14 07:11:27.744192+01	5219369c-9afd-488f-b7a1-59234760eef7	6	18
\.


--
-- Data for Name: exams_examattempt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_examattempt (id, score, status, verification_token, is_submitted, retake_allowed, question_order, remaining_seconds, interruption_reason, started_at, last_activity_at, completed_at, exam_id, student_id) FROM stdin;
20	12	archived	b44acb49-efc6-4e06-b701-bb9b1500485f	f	f	[]	300		2026-02-19 12:39:57.539459+01	2026-02-19 12:40:23.896313+01	2026-02-19 12:40:23.854265+01	50	22
21	12	submitted	d876694c-de69-463b-ba0d-842bb2e3a1eb	f	f	[]	300		2026-02-19 12:45:27.407927+01	2026-02-19 12:45:49.285674+01	2026-02-19 12:45:49.244048+01	50	22
\.


--
-- Data for Name: dashboards_attempthistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_attempthistory (id, attempt_number, score, total_marks, percentage, status, time_taken, submitted_at, can_retake, retake_available_from, attempt_id, exam_id, student_id) FROM stdin;
\.


--
-- Data for Name: dashboards_bulkexportjob; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_bulkexportjob (id, export_type, status, file_format, export_file, created_at, completed_at, exam_id, exported_by_id) FROM stdin;
\.


--
-- Data for Name: dashboards_bulkimportjob; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_bulkimportjob (id, import_type, csv_file, status, total_rows, successful_rows, failed_rows, error_log, started_at, completed_at, created_at, created_by_id) FROM stdin;
1	questions	bulk_imports/test_questions.xlsx	completed	1	1	0		2026-02-04 06:40:47.271+01	2026-02-04 06:40:47.356+01	2026-02-04 06:40:47.277+01	1
2	questions	bulk_imports/test_questions.docx	completed	1	1	0		2026-02-04 06:40:47.519+01	2026-02-04 06:40:47.624+01	2026-02-04 06:40:47.523+01	1
3	questions	bulk_imports/question_template.xlsx	completed	1	1	0		2026-02-04 07:17:25.179+01	2026-02-04 07:17:25.319+01	2026-02-04 07:17:25.187+01	1
4	questions	bulk_imports/test_questions.csv	failed	1	0	1	No data found in file	2026-02-04 07:51:38.89+01	2026-02-04 07:51:38.911+01	2026-02-04 07:51:38.892+01	1
5	questions	bulk_imports/test_questions_20dLOrN.csv	completed	2	2	0		2026-02-04 07:52:14.65+01	2026-02-04 07:52:14.716+01	2026-02-04 07:52:14.655+01	1
6	questions	bulk_imports/question_template_3.xlsx	completed	1	1	0		2026-02-04 07:57:02.741+01	2026-02-04 07:57:02.838+01	2026-02-04 07:57:02.747+01	1
7	questions	bulk_imports/question_template_3_kaZyGNn.xlsx	completed	1	1	0		2026-02-04 08:10:20.081+01	2026-02-04 08:10:20.611+01	2026-02-04 08:10:20.084+01	1
8	questions	bulk_imports/question_template_4.xlsx	failed	1	0	1	Row 1: Subject 'Yoruba' not found	2026-02-07 22:05:30.512+01	2026-02-07 22:05:30.591+01	2026-02-07 22:05:30.525+01	1
\.


--
-- Data for Name: dashboards_certificate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_certificate (id, certificate_number, score, total_marks, percentage, grade, issued_at, pdf_file, is_digitally_verified, verification_code, attempt_id, exam_id, student_id) FROM stdin;
\.


--
-- Data for Name: dashboards_certificatetemplate; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_certificatetemplate (id, name, school, logo, background, text_color, font_family, custom_message, is_default, created_at, created_by_id) FROM stdin;
1	Default	School of Excellence			#333333	Arial		t	2026-02-09 12:01:30.431+01	\N
\.


--
-- Data for Name: dashboards_chatroom; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_chatroom (id, name, created_at, created_by_id, room_type) FROM stdin;
1	Staff Conference	2026-02-05 07:50:46.418+01	1	GROUP
2	State of Affair	2026-02-05 08:05:19.017+01	1	GROUP
3	State of Affairs	2026-02-06 22:51:50.906+01	1	GROUP
4	class ordering	2026-02-06 23:40:09.328+01	1	GROUP
5	party	2026-02-06 23:45:30.006+01	1	CONFERENCE
\.


--
-- Data for Name: dashboards_chatroom_participants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_chatroom_participants (id, chatroom_id, user_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	2	1
5	2	2
6	2	3
7	3	1
8	4	1
9	4	3
10	5	1
11	5	3
\.


--
-- Data for Name: dashboards_chatroommessage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_chatroommessage (id, message, created_at, room_id, sender_id, attachment) FROM stdin;
1	hi	2026-02-05 08:13:16.73+01	2	1	
2	hello	2026-02-06 23:41:02.408+01	4	1	
3		2026-02-06 23:45:57.571+01	5	1	room_attachments/about-school.png
4	fhgfh	2026-02-07 01:27:05.28+01	5	1	
\.


--
-- Data for Name: dashboards_chatroomreadstatus; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_chatroomreadstatus (id, last_read_at, room_id, user_id) FROM stdin;
1	2026-02-06 23:47:10.886+01	2	1
2	2026-02-07 00:36:21.854+01	4	1
3	2026-02-07 01:27:05.304+01	5	1
4	2026-02-08 23:14:13.366+01	1	1
6	2026-02-09 15:28:43.222+01	2	3
7	2026-02-09 15:28:35.501+01	4	3
8	2026-02-09 15:28:37.223+01	5	3
5	2026-02-13 20:14:14.565597+01	3	1
\.


--
-- Data for Name: dashboards_examanalytics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_examanalytics (id, total_attempts, total_passed, average_score, highest_score, lowest_score, average_time_taken, pass_rate, last_updated, exam_id) FROM stdin;
4	1	0	4	4	4	0	0	2026-02-09 15:40:35.094+01	48
5	1	0	12	12	12	71	0	2026-02-11 13:45:35.385+01	50
\.


--
-- Data for Name: dashboards_examschedule; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_examschedule (id, scheduled_date, auto_open, auto_close, close_at, auto_submit_at_time, notify_before_minutes, created_at, exam_id) FROM stdin;
\.


--
-- Data for Name: dashboards_gradingrubric; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_gradingrubric (id, name, description, total_points, is_published, created_at, created_by_id, exam_id) FROM stdin;
\.


--
-- Data for Name: dashboards_notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_notification (id, title, message, category, is_read, created_at, recipient_id, related_exam_id) FROM stdin;
1	Broadcast: Texbook purchase	Books are available, come and buy	info	f	2026-02-05 08:25:44.3+01	4	\N
2	Broadcast: Texbook purchase	Books are available, come and buy	info	f	2026-02-05 08:25:44.3+01	6	\N
3	Broadcast: Texbook purchase	Books are available, come and buy	info	f	2026-02-05 08:25:44.3+01	7	\N
4	Broadcast: Texbook purchase	Books are available, come and buy	info	f	2026-02-05 08:25:44.3+01	8	\N
5	Broadcast: hello	how are you\r\n	info	f	2026-02-05 08:27:05.743+01	6	\N
\.


--
-- Data for Name: dashboards_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_permission (id, code, name, description, category) FROM stdin;
\.


--
-- Data for Name: dashboards_questioncategory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_questioncategory (id, name, description, color, created_at, created_by_id) FROM stdin;
\.


--
-- Data for Name: exams_subject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_subject (id, name, description, department, is_active, created_at, created_by_id) FROM stdin;
1	Mathematics			t	2026-01-31 15:53:24.718+01	1
2	English Language	Subject for English Language	General	t	2026-02-04 02:11:34.694+01	1
4	Civic Education	Subject for Civic Education	General	t	2026-02-04 02:11:34.88+01	1
5	Biology	Biology Subject	General	t	2026-02-04 06:27:08.37+01	1
6	Chemistry	Chemistry Subject		t	2026-02-04 06:27:08.388+01	1
7	Physics	Physics Subject		t	2026-02-04 06:27:08.406+01	1
8	Economics	Economics Subject		t	2026-02-04 06:27:08.423+01	1
9	Government	Government Subject		t	2026-02-04 06:27:08.442+01	1
10	Geography	Geography Subject		t	2026-02-04 06:27:08.461+01	1
11	Mathematics Verification			t	2026-02-04 07:51:38.873+01	\N
12	Yoruba	Ede Yoruba	General	t	2026-02-08 04:24:56.818+01	\N
\.


--
-- Data for Name: dashboards_questionbank; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_questionbank (id, text, question_type, marks, difficulty, explanation, image, is_published, usage_count, created_at, updated_at, created_by_id, category_id, school_class_id, subject_id) FROM stdin;
1	Who is Nigeria President	objective	1	easy			t	0	2026-02-01 16:14:39.254+01	2026-02-01 16:14:39.254+01	1	\N	\N	\N
2	Who is Nigeria President	objective	1	easy			t	0	2026-02-01 16:17:38.172+01	2026-02-01 16:19:06.674+01	1	\N	\N	\N
3	Excel Test Question	objective	5	hard			t	0	2026-02-04 06:40:47.307+01	2026-02-04 06:40:47.307+01	1	\N	\N	\N
4	Word Test Question	objective	5	medium			t	0	2026-02-04 06:40:47.573+01	2026-02-04 06:40:47.573+01	1	\N	\N	\N
5	Who is Nigeria President	objective	1	medium			t	0	2026-02-04 07:17:25.228+01	2026-02-04 07:17:25.228+01	1	\N	\N	\N
6	Test Q1 Verification	objective	1	medium			t	0	2026-02-04 07:52:14.677+01	2026-02-04 07:52:14.677+01	1	\N	14	11
7	Test Q2 Verification	subjective	5	medium			t	0	2026-02-04 07:52:14.699+01	2026-02-04 07:52:14.699+01	1	\N	14	11
8	What's 5+6	objective	1	medium			t	0	2026-02-04 07:57:02.787+01	2026-02-04 07:57:02.787+01	1	\N	9	1
9	What's 5+6	objective	1	medium			t	0	2026-02-04 08:10:20.55+01	2026-02-04 08:10:20.55+01	1	\N	9	1
\.


--
-- Data for Name: dashboards_questiontag; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_questiontag (id, name, created_at) FROM stdin;
\.


--
-- Data for Name: dashboards_questionbank_tags; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_questionbank_tags (id, questionbank_id, questiontag_id) FROM stdin;
\.


--
-- Data for Name: dashboards_questionchoice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_questionchoice (id, text, is_correct, "order", question_id) FROM stdin;
1	Buhari	f	0	1
2	Chisom	f	1	1
3	Jonathan	f	2	1
4	Tinubu	t	3	1
17	Buhari	f	0	2
18	Chisom	f	1	2
19	Jonathan	f	2	2
20	Tinubu	t	3	2
21	Option A	f	1	3
22	Option B	t	2	3
23	Option X	t	1	4
24	Option Y	f	2	4
25	Obasanjo	f	1	5
26	Tinubu	t	2	5
27	Abacha	f	3	5
28	Buhari	f	4	5
29	13	f	1	8
30	11	t	2	8
31	13	f	1	9
32	11	t	2	9
\.


--
-- Data for Name: dashboards_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_role (id, name, role_type, description, is_active, created_at, created_by_id) FROM stdin;
\.


--
-- Data for Name: dashboards_rolepermission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_rolepermission (id, permission_id, role_id) FROM stdin;
\.


--
-- Data for Name: dashboards_rubriccriteria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_rubriccriteria (id, name, description, max_points, "order", rubric_id) FROM stdin;
\.


--
-- Data for Name: dashboards_rubricgrade; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_rubricgrade (id, total_score, feedback, graded_at, attempt_id, graded_by_id, rubric_id) FROM stdin;
\.


--
-- Data for Name: dashboards_rubricscore; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_rubricscore (id, level, points, description, criteria_id) FROM stdin;
\.


--
-- Data for Name: dashboards_rubriccriteriagrade; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_rubriccriteriagrade (id, points_awarded, comment, criteria_id, rubric_grade_id, selected_score_id) FROM stdin;
\.


--
-- Data for Name: dashboards_schedulednotification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_schedulednotification (id, notification_sent_at, was_successful, exam_id, student_id) FROM stdin;
\.


--
-- Data for Name: dashboards_studentperformance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_studentperformance (id, attempt_number, score, total_marks, percentage, time_taken, status, attempted_at, exam_id, student_id) FROM stdin;
\.


--
-- Data for Name: dashboards_userrole; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.dashboards_userrole (id, assigned_at, expires_at, assigned_by_id, role_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-01-31 15:48:54.928+01	1	idrees - Admin	2	[{"changed": {"fields": ["First name", "Last name", "Role"]}}]	24	1
2	2026-01-31 15:54:45.406+01	1	idrees - Admin	2	[{"changed": {"fields": ["Email address", "Is approved"]}}]	24	1
3	2026-01-31 15:56:38.276+01	2	admin - Admin	2	[{"changed": {"fields": ["Role", "Last login"]}}]	24	1
4	2026-01-31 15:57:40.428+01	3	teacher1 - Teacher	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Role", "Student class", "Last login"]}}]	24	1
5	2026-01-31 15:58:23.651+01	4	teacher2 - Parent	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Student class", "Last login"]}}]	24	1
6	2026-01-31 16:00:59.11+01	20	student10 - Student	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Role", "Student class", "Parent/Guardian", "Last login"]}}]	24	1
7	2026-01-31 16:02:05.129+01	19	student9 - Student	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Role", "Student class", "Parent/Guardian", "Last login"]}}]	24	1
8	2026-01-31 16:02:59.346+01	18	student8 - Student	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Role", "Parent/Guardian", "Last login"]}}]	24	1
9	2026-01-31 16:20:55.189+01	20	student10 - Student	2	[]	24	1
10	2026-01-31 19:54:27.83+01	1	JSS1	2	[{"changed": {"fields": ["Level", "Academic year", "Teacher", "Assistant teacher"]}}]	16	1
11	2026-02-01 16:02:51.872+01	21	tola - Student	2	[{"changed": {"fields": ["Username", "Phone number", "Address", "Role", "Student class", "Parent/Guardian", "Is active", "Is approved", "Last login"]}}]	24	1
12	2026-02-01 16:03:45.996+01	22	jade - Student	2	[{"changed": {"fields": ["Phone number", "Address", "Role", "Student class", "Parent/Guardian", "Is active", "Is approved", "Last login"]}}]	24	1
13	2026-02-01 16:04:32.521+01	23	jane - Student	2	[{"changed": {"fields": ["Role", "Parent/Guardian", "Is approved", "Last login"]}}]	24	1
14	2026-02-01 16:38:19.453+01	23	jane - Student	2	[{"changed": {"fields": ["password"]}}]	24	1
15	2026-02-01 16:38:21.578+01	23	jane - Student	2	[{"changed": {"fields": ["password"]}}]	24	1
16	2026-02-01 16:38:22.498+01	23	jane - Student	2	[{"changed": {"fields": ["password"]}}]	24	1
17	2026-02-01 16:38:23.34+01	23	jane - Student	2	[{"changed": {"fields": ["password"]}}]	24	1
18	2026-02-01 17:04:18.518+01	18	student8 - Student	2	[{"changed": {"fields": ["password"]}}]	24	1
19	2026-02-01 17:37:11.61+01	12	student2 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
20	2026-02-01 17:37:55.678+01	12	bola - Parent	2	[{"changed": {"fields": ["Username", "Last login"]}}]	24	1
21	2026-02-01 17:38:27.272+01	18	sola - Student	2	[{"changed": {"fields": ["Username"]}}]	24	1
22	2026-02-01 17:40:04.446+01	12	bola - Student	2	[{"changed": {"fields": ["Role"]}}]	24	1
23	2026-02-01 18:02:04.008+01	2	First Term English Language	3		9	1
24	2026-02-04 16:54:39.729+01	6	parent1 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
25	2026-02-04 16:55:04.631+01	6	parent1 - Parent	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Last login"]}}]	24	1
26	2026-02-04 16:55:26.489+01	7	parent2 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
27	2026-02-04 17:58:58.815+01	23	jane - Student	2	[]	24	1
28	2026-02-10 21:23:26.337+01	4	teacher2 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
29	2026-02-10 21:24:28.233+01	4	teacher2 - Teacher	2	[{"changed": {"fields": ["Role", "Student class"]}}]	24	1
30	2026-02-10 21:25:01.808+01	5	teacher3 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
31	2026-02-10 21:26:03.206+01	5	teacher3 - Teacher	2	[{"changed": {"fields": ["First name", "Last name", "Phone number", "Address", "Role", "Student class", "Last login"]}}]	24	1
32	2026-02-10 21:27:15.6+01	18	sola - Student	2	[{"changed": {"fields": ["Student class"]}}]	24	1
33	2026-02-11 05:51:53.85+01	6	parent1 - Parent	2	[{"changed": {"fields": ["password"]}}]	24	1
34	2026-02-11 05:52:16.871+01	6	parent1 - Parent	2	[]	24	1
35	2026-02-11 05:54:11.299+01	6	baba - Parent	2	[{"changed": {"fields": ["Username"]}}]	24	1
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2026-02-13 14:38:55.032385+01
2	contenttypes	0002_remove_content_type_name	2026-02-13 14:38:55.04501+01
3	auth	0001_initial	2026-02-13 14:38:55.169353+01
4	auth	0002_alter_permission_name_max_length	2026-02-13 14:38:55.178449+01
5	auth	0003_alter_user_email_max_length	2026-02-13 14:38:55.186303+01
6	auth	0004_alter_user_username_opts	2026-02-13 14:38:55.196421+01
7	auth	0005_alter_user_last_login_null	2026-02-13 14:38:55.202496+01
8	auth	0006_require_contenttypes_0002	2026-02-13 14:38:55.204527+01
9	auth	0007_alter_validators_add_error_messages	2026-02-13 14:38:55.215857+01
10	auth	0008_alter_user_username_max_length	2026-02-13 14:38:55.22415+01
11	auth	0009_alter_user_last_name_max_length	2026-02-13 14:38:55.231749+01
12	auth	0010_alter_group_name_max_length	2026-02-13 14:38:55.244339+01
13	auth	0011_update_proxy_permissions	2026-02-13 14:38:55.251265+01
14	auth	0012_alter_user_first_name_max_length	2026-02-13 14:38:55.260656+01
15	accounts	0001_initial	2026-02-13 14:38:55.402173+01
16	exams	0001_initial	2026-02-13 14:38:56.34479+01
17	accounts	0002_initial	2026-02-13 14:38:56.453959+01
18	admin	0001_initial	2026-02-13 14:38:56.519629+01
19	admin	0002_logentry_remove_auto_add	2026-02-13 14:38:56.549021+01
20	admin	0003_logentry_add_action_flag_choices	2026-02-13 14:38:56.582328+01
21	brillspay	0001_initial	2026-02-13 14:38:57.161642+01
22	brillspay	0002_orderitem_product	2026-02-13 14:38:57.219628+01
23	exams	0002_alter_exam_school_class	2026-02-13 14:38:57.267988+01
24	dashboards	0001_initial	2026-02-13 14:38:59.585559+01
25	dashboards	0002_questionbank_school_class_questionbank_subject	2026-02-13 14:38:59.734807+01
26	dashboards	0003_chatroom_chatroommessage	2026-02-13 14:39:00.058484+01
27	dashboards	0004_chatroommessage_attachment	2026-02-13 14:39:00.122157+01
28	dashboards	0005_chatroom_room_type	2026-02-13 14:39:00.189257+01
29	dashboards	0006_chatroomreadstatus	2026-02-13 14:39:00.307897+01
30	exams	0003_broadcast_recipients_broadcast_target_role	2026-02-13 14:39:00.484816+01
31	exams	0004_chatmessage_attachment	2026-02-13 14:39:00.552907+01
32	payroll	0001_initial	2026-02-13 14:39:01.606207+01
33	payroll	0002_remove_payee_address_remove_payee_date_of_employment_and_more	2026-02-13 14:39:01.853406+01
34	payroll	0003_salarycomponent_tax_rate	2026-02-13 14:39:01.861452+01
35	payroll	0004_remove_salarycomponent_is_taxable_and_more	2026-02-13 14:39:01.887139+01
36	leaves	0001_initial	2026-02-13 14:39:02.040047+01
37	loans	0001_initial	2026-02-13 14:39:02.376888+01
38	payroll	0005_payrollrecord_is_processed_and_more	2026-02-13 14:39:02.424463+01
39	pickup	0001_initial	2026-02-13 14:39:02.782162+01
40	sessions	0001_initial	2026-02-13 14:39:02.8151+01
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
na8r1iuh7nn7d8kwjz2pik1qr5egby14	.eJxVjDsOwjAQBe_iGlnxyo6zlPScwXrrDw6gRIqTCnF3iJQC2jcz76UCtrWGreUljEmdlVGn300QH3naQbpjus06ztO6jKJ3RR-06euc8vNyuH8HFa1-ay_WAD6id1wKOfGRI4CSDPLgyAp76pJYggw9kyFnSWznGczkod4fAXM3-w:1vrZBd:tMAJHMur1No-ntvTUnHEq82-KMkSjzqF5Ae71-9tUYk	2026-03-01 11:17:09.009647+01
2fk5d2lbdvuqt9vkuzfs9k55hnvwnyzn	.eJxVjMsOwiAQRf-FtSEdKMK4dN9vIDNlkKqBpI-V8d-1SRe6veec-1KRtrXEbZE5TkldVFCn341pfEjdQbpTvTU9trrOE-td0Qdd9NCSPK-H-3dQaCnfuiMGgmBDh6YTA-TZeJfEUuoBz5YzejAZe2cheyEPGRjsSOi4l4zq_QHPLDeb:1vt2ZF:pMJUBOGcMSJXL9SVMM1OXWo8pzsIRjGPtF0Kz2rnFGQ	2026-03-05 12:51:37.198347+01
\.


--
-- Data for Name: exams_broadcast; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_broadcast (id, title, message, created_at, sender_id, target_class_id, target_role) FROM stdin;
1	School Fees	Pay yourschool fee	2026-02-04 18:54:41.803+01	1	11	
2	Texbook purchase	Books are available, come and buy	2026-02-05 08:19:09.935+01	1	\N	parents
3	Texbook purchase	Books are available, come and buy	2026-02-05 08:25:44.227+01	1	\N	parents
4	hello	how are you\r\n	2026-02-05 08:27:05.671+01	1	2	parents
5	Read your books	Read your books	2026-02-09 15:14:07.761+01	1	\N	students
6	Punctuality	Come to school early	2026-02-09 15:14:50.816+01	1	\N	students
\.


--
-- Data for Name: exams_broadcast_recipients; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_broadcast_recipients (id, broadcast_id, user_id) FROM stdin;
1	2	8
2	2	4
3	2	6
4	2	7
5	3	8
6	3	4
7	3	6
8	3	7
9	4	6
\.


--
-- Data for Name: exams_chatmessage; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_chatmessage (id, message, is_read, created_at, recipient_id, sender_id, attachment) FROM stdin;
1	Hi 	t	2026-01-31 17:55:41.575+01	3	1	
16	hello sir	f	2026-02-09 15:30:50.022+01	2	3	
17		f	2026-02-09 15:31:01.336+01	2	3	chat_attachments/CERT-F6CE28837F0A-20260209_16.pdf
\.


--
-- Data for Name: exams_question; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_question (id, text, type, marks, "order", exam_id) FROM stdin;
142	Which of the following is NOT a valid variable name in Python?	objective	5	1	47
143	What is the time complexity of binary search?	objective	5	2	47
144	Which data structure uses LIFO (Last In First Out) principle?	objective	5	3	47
145	What does HTML stand for?	objective	5	4	47
146	In which year did World War II end?	objective	2	1	48
147	Who was the first person to walk on the moon?	objective	2	2	48
148	Analyze the primary causes of the Cold War. Discuss at least two major factors.	subjective	10	3	48
149	Describe the impact of the Industrial Revolution on urban life.	subjective	10	4	48
150	What is the unit of Force in the SI system?	objective	2	1	49
151	According to Newton's Second Law, Force equals:	objective	2	2	49
152	Explain the concept of Conservation of Energy with a real-world example.	subjective	15	3	49
153	Derive the equation for the period of a simple pendulum.	subjective	15	4	49
154	what is 2+3	objective	10	1	50
155	what is 4-2	objective	1	2	50
156	wat is 3*4	objective	1	3	50
\.


--
-- Data for Name: exams_choice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_choice (id, text, is_correct, question_id) FROM stdin;
328	my_variable	f	142
329	_variable	f	142
330	2variable	t	142
331	variable2	f	142
332	O(n)	f	143
333	O(log n)	t	143
334	O(n^2)	f	143
335	O(1)	f	143
336	Queue	f	144
337	Stack	t	144
338	Tree	f	144
339	Linked List	f	144
340	Hyper Text Markup Language	t	145
341	High Tech Modern Language	f	145
342	Hyper Transfer Mark Language	f	145
343	Home Tool Markup Language	f	145
344	1943	f	146
345	1944	f	146
346	1945	t	146
347	1946	f	146
348	Yuri Gagarin	f	147
349	Neil Armstrong	t	147
350	Buzz Aldrin	f	147
351	Michael Collins	f	147
352	Joule	f	150
353	Newton	t	150
354	Watt	f	150
355	Pascal	f	150
356	Mass x Velocity	f	151
357	Mass x Acceleration	t	151
358	Mass / Acceleration	f	151
359	Acceleration / Mass	f	151
360	5	t	154
361	4	f	154
362	45	f	154
363	32	f	154
364	0	f	155
365	1	f	155
366	2	t	155
367	3	f	155
368	34	f	156
369	43	f	156
370	12	t	156
371	1	f	156
\.


--
-- Data for Name: exams_examaccess; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_examaccess (id, reason, via_payment, granted_at, exam_id, granted_by_id, student_id) FROM stdin;
1	Special access granted for testing	f	2026-02-09 16:53:23.505+01	50	\N	12
\.


--
-- Data for Name: exams_notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_notification (id, title, message, is_read, created_at, related_exam, recipient_id, sender_id) FROM stdin;
29	Broadcast: Read your books	Read your books	t	2026-02-09 15:14:07.829+01	\N	12	1
30	Broadcast: Read your books	Read your books	t	2026-02-09 15:14:07.829+01	\N	18	1
31	Broadcast: Read your books	Read your books	t	2026-02-09 15:14:07.829+01	\N	19	1
32	Broadcast: Read your books	Read your books	t	2026-02-09 15:14:07.829+01	\N	20	1
33	Broadcast: Read your books	Read your books	t	2026-02-09 15:14:07.829+01	\N	21	1
36	Broadcast: Punctuality	Come to school early	t	2026-02-09 15:14:50.881+01	\N	12	1
37	Broadcast: Punctuality	Come to school early	t	2026-02-09 15:14:50.881+01	\N	18	1
38	Broadcast: Punctuality	Come to school early	t	2026-02-09 15:14:50.881+01	\N	19	1
39	Broadcast: Punctuality	Come to school early	t	2026-02-09 15:14:50.881+01	\N	20	1
40	Broadcast: Punctuality	Come to school early	t	2026-02-09 15:14:50.881+01	\N	21	1
47	Exam Graded	Your answer to "Analyze the primary causes of the Cold War. Discus..." has been graded (10/10 marks)	f	2026-02-11 12:37:13.87+01	48	12	3
48	Exam Graded	Your answer to "Describe the impact of the Industrial Revolution o..." has been graded (10/10 marks)	f	2026-02-11 12:37:52.393+01	48	12	3
49	Exam Graded	Your answer to "Analyze the primary causes of the Cold War. Discus..." has been graded (10/10 marks)	f	2026-02-11 12:43:21.774+01	48	12	3
50	Exam Graded	Your answer to "Describe the impact of the Industrial Revolution o..." has been graded (10/10 marks)	f	2026-02-11 12:43:37.531+01	48	12	3
51	Exam Graded	Your answer to "Analyze the primary causes of the Cold War. Discus..." has been graded (10/10 marks)	f	2026-02-12 03:40:17.007+01	48	12	3
52	Exam Graded	Your answer to "Describe the impact of the Industrial Revolution o..." has been graded (10/10 marks)	f	2026-02-12 03:40:23.797+01	48	12	3
53	exam_started	Oladimeji Ademola started exam: First Term Exam Math	f	2026-02-19 12:39:57.569262+01	50	3	22
54	Exam Submitted	Oladimeji Ademola submitted exam: First Term Exam Math	f	2026-02-19 12:40:23.90659+01	50	3	22
56	exam_started	Oladimeji Ademola started exam: First Term Exam Math	f	2026-02-19 12:45:27.415624+01	50	3	22
57	Exam Submitted	Oladimeji Ademola submitted exam: First Term Exam Math	f	2026-02-19 12:45:49.295267+01	50	3	22
\.


--
-- Data for Name: exams_ptarequest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_ptarequest (id, request_type, title, message, status, scheduled_time, created_at, updated_at, parent_id, recipient_id) FROM stdin;
\.


--
-- Data for Name: exams_retakerequest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_retakerequest (id, reason, status, created_at, updated_at, exam_id, reviewed_by_id, student_id) FROM stdin;
3	\N	approved	2026-02-09 16:12:52.243+01	2026-02-09 16:58:46.453+01	50	1	22
4	no issue, just flexing\r\n	approved	2026-02-19 12:42:00.002364+01	2026-02-19 12:44:11.051202+01	50	1	22
\.


--
-- Data for Name: exams_studentanswer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_studentanswer (id, answer_text, attempt_id, question_id, selected_choice_id) FROM stdin;
46		20	154	360
47		20	155	366
48		20	156	370
49		21	154	360
50		21	156	370
51		21	155	366
\.


--
-- Data for Name: exams_subject_classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_subject_classes (id, subject_id, schoolclass_id) FROM stdin;
1	1	3
2	1	4
3	1	5
4	1	9
5	1	11
6	1	12
7	1	13
8	2	2
9	2	6
10	2	11
11	2	12
12	2	13
13	4	10
14	4	11
15	4	12
16	4	13
17	5	9
18	5	10
19	5	13
20	6	1
21	6	11
22	6	12
23	6	6
24	7	1
25	7	2
26	7	4
27	8	3
28	8	5
29	9	9
30	9	2
31	9	4
32	9	6
33	10	1
34	10	3
35	10	4
36	10	5
37	10	10
38	12	2
\.


--
-- Data for Name: exams_subjectivemark; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_subjectivemark (id, score, marked_at, answer_id, marked_by_id) FROM stdin;
\.


--
-- Data for Name: exams_systemlog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_systemlog (id, level, source, message, created_at) FROM stdin;
1	INFO		Sample log entry 0	2026-01-31 15:53:24.386+01
2	INFO		Sample log entry 1	2026-01-31 15:53:24.402+01
3	INFO		Sample log entry 2	2026-01-31 15:53:24.417+01
4	INFO		Sample log entry 3	2026-01-31 15:53:24.433+01
5	INFO		Sample log entry 4	2026-01-31 15:53:24.448+01
6	INFO		Sample log entry 5	2026-01-31 15:53:24.465+01
7	INFO		Sample log entry 6	2026-01-31 15:53:24.48+01
8	INFO		Sample log entry 7	2026-01-31 15:53:24.496+01
9	INFO		Sample log entry 8	2026-01-31 15:53:24.51+01
10	INFO		Sample log entry 9	2026-01-31 15:53:24.526+01
11	INFO		Sample log entry 10	2026-01-31 15:53:24.542+01
12	INFO		Sample log entry 11	2026-01-31 15:53:24.558+01
13	INFO		Sample log entry 12	2026-01-31 15:53:24.573+01
14	INFO		Sample log entry 13	2026-01-31 15:53:24.589+01
15	INFO		Sample log entry 14	2026-01-31 15:53:24.606+01
16	INFO		Sample log entry 15	2026-01-31 15:53:24.622+01
17	INFO		Sample log entry 16	2026-01-31 15:53:24.642+01
18	INFO		Sample log entry 17	2026-01-31 15:53:24.659+01
19	INFO		Sample log entry 18	2026-01-31 15:53:24.675+01
20	INFO		Sample log entry 19	2026-01-31 15:53:24.689+01
21	INFO	Chat	Message sent from idrees (Admin) to teacher1 (Teacher)	2026-01-31 17:55:41.597+01
22	INFO		Student jane started exam: First Term English Language	2026-02-01 16:41:06.229+01
23	INFO		Student student8 started exam: First Term English Language	2026-02-01 17:07:15.922+01
24	INFO		Student bola started exam: First Term English Language	2026-02-01 17:42:35.29+01
25	INFO		Student bola started exam: First Term Exam Math	2026-02-01 18:16:30.63+01
26	INFO		Student jane started exam: First Term Exam Math	2026-02-01 18:34:48.311+01
27	INFO	Chat	Message sent from idrees (Admin) to teacher1 (Teacher)	2026-02-01 22:24:08.164+01
28	INFO	Chat	Message sent from teacher1 (Teacher) to idrees (Admin)	2026-02-01 22:29:56.06+01
29	INFO	Broadcast	Broadcast 'School Fees' sent by idrees to JSS 1	2026-02-04 18:54:41.826+01
30	INFO		Student jane started exam: English Language - JSS2 Term 1 Exam	2026-02-05 06:41:23.192+01
31	INFO		Student jane started exam: Government - JSS2 Term 1 Exam	2026-02-05 06:56:04.418+01
32	INFO	Broadcast	Broadcast 'Texbook purchase' sent by idrees to All Students	2026-02-05 08:19:09.99+01
33	INFO	Broadcast	Broadcast 'Texbook purchase' sent by idrees to All Students	2026-02-05 08:25:44.284+01
34	INFO	Broadcast	Broadcast 'hello' sent by idrees to JSS2	2026-02-05 08:27:05.726+01
35	INFO		Student jade started exam: Mathematics - JSS3 Term 1 Exam	2026-02-05 08:36:57.51+01
36	INFO		Student jade started exam: Geography - JSS3 Term 1 Exam	2026-02-05 08:50:03.068+01
37	INFO		Exam interrupted by jade: Mathematics - JSS3 Term 1 Exam	2026-02-05 09:06:13.429+01
38	INFO		Exam interrupted by jade: Geography - JSS3 Term 1 Exam	2026-02-05 09:12:43.518+01
39	INFO		Student jade started exam: Economics - JSS3 Term 1 Exam	2026-02-05 09:27:45.178+01
40	INFO		Student jade submitted exam: Economics - JSS3 Term 1 Exam	2026-02-05 09:28:52.667+01
41	INFO		Student jade submitted exam: Geography - JSS3 Term 1 Exam	2026-02-05 09:32:33.184+01
42	INFO		Student jade started exam: Geography - JSS3 Term 1 Exam	2026-02-05 09:38:02.852+01
43	INFO		Student jade submitted exam: Geography - JSS3 Term 1 Exam	2026-02-05 09:38:53.595+01
44	INFO		Student jade started exam: Geography - JSS3 Term 1 Exam	2026-02-05 09:56:23.865+01
45	INFO		Exam interrupted by jade: Geography - JSS3 Term 1 Exam	2026-02-05 09:56:36.957+01
46	INFO		Student jade submitted exam: Geography - JSS3 Term 1 Exam	2026-02-05 09:57:33.437+01
47	INFO		Student jade started exam: Economics - JSS3 Term 1 Exam	2026-02-05 10:07:21.682+01
48	INFO		Student jade submitted exam: Economics - JSS3 Term 1 Exam	2026-02-05 10:07:54.801+01
49	INFO	Chat	Message sent from teacher1 (Teacher) to idrees (Admin)	2026-02-05 10:46:25.964+01
50	INFO		idrees graded subjective answer (attempt 13)	2026-02-05 11:51:44.97+01
51	INFO		idrees graded subjective answer (attempt 10)	2026-02-05 11:52:39.994+01
52	INFO		idrees graded subjective answer (attempt 9)	2026-02-05 11:53:46.468+01
53	INFO		idrees graded subjective answer (attempt 11)	2026-02-05 11:53:48.819+01
54	INFO		idrees graded subjective answer (attempt 12)	2026-02-05 11:53:50.818+01
55	INFO		Student jane started exam: Physics - JSS2 Term 1 Exam	2026-02-05 15:11:32.239+01
56	INFO		Student jane submitted exam: Physics - JSS2 Term 1 Exam	2026-02-05 15:12:52.966+01
57	INFO	Chat	DM sent from idrees to teacher1	2026-02-06 23:26:18.581+01
58	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:20:51.696+01
59	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:21:00.585+01
60	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:43:00.632+01
61	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:43:22.673+01
62	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:53:38.514+01
63	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:55:24.657+01
64	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 00:59:16.722+01
65	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 01:19:54.254+01
66	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 01:25:40.604+01
67	INFO	Chat	DM sent from idrees to teacher1	2026-02-07 01:25:53.822+01
68	INFO		idrees graded subjective answer (attempt 13)	2026-02-07 21:50:44.056+01
69	INFO		idrees graded subjective answer (attempt 10)	2026-02-07 21:50:49.871+01
70	INFO		idrees graded subjective answer (attempt 10)	2026-02-07 21:51:18.167+01
71	INFO	Broadcast	Broadcast 'Read your books' sent by idrees to All Students	2026-02-09 15:14:07.804+01
72	INFO	Broadcast	Broadcast 'Punctuality' sent by idrees to All Students	2026-02-09 15:14:50.855+01
73	INFO	Chat	DM sent from teacher1 to admin	2026-02-09 15:30:50.046+01
74	INFO	Chat	DM sent from teacher1 to admin	2026-02-09 15:31:01.425+01
75	INFO		Student jade started exam: First Term Exam Math	2026-02-09 16:11:24.056+01
76	INFO		Student jade submitted exam: First Term Exam Math	2026-02-09 16:12:35.389+01
77	INFO		Student jade started exam: First Term Exam Math	2026-02-09 16:59:47.842+01
78	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-11 12:37:13.872+01
79	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-11 12:37:52.394+01
80	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-11 12:43:21.776+01
81	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-11 12:43:37.532+01
82	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-12 03:40:17.008+01
83	INFO		teacher1 graded subjective answer (attempt 17)	2026-02-12 03:40:23.797+01
84	INFO		Student jade started exam: First Term Exam Math	2026-02-19 12:39:57.557161+01
85	INFO		Student jade submitted exam: First Term Exam Math	2026-02-19 12:40:23.898324+01
86	INFO		Student jade started exam: First Term Exam Math	2026-02-19 12:45:27.411446+01
87	INFO		Student jade submitted exam: First Term Exam Math	2026-02-19 12:45:49.287879+01
\.


--
-- Data for Name: leaves_leavetype; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.leaves_leavetype (id, name, annual_days) FROM stdin;
1	Sick Leave	7
2	Paternity Leave	7
3	Maternity Leave	40
\.


--
-- Data for Name: payroll_payee; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_payee (id, payee_type, reference_code, is_confirmed, is_active, created_at, user_id) FROM stdin;
1	teacher	PAYEE-ADDC4F96	f	t	2026-02-05 10:38:59.614+01	3
2	teacher	PAYEE-93F5EE99	f	t	2026-02-10 21:46:33.278+01	4
3	admin	PAYEE-2690828E	f	t	2026-02-11 11:50:58.497+01	1
\.


--
-- Data for Name: leaves_leaverequest; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.leaves_leaverequest (id, start_date, end_date, reason, status, reviewed_at, created_at, payee_id, reviewed_by_id, leave_type_id) FROM stdin;
1	2026-02-20	2026-03-05	mo bimo	rejected	2026-02-09 09:41:17.552+01	2026-02-05 10:56:40.701+01	1	1	2
2	2026-02-09	2026-02-11	omo	approved	2026-02-09 16:13:27.488+01	2026-02-09 15:29:44.839+01	1	1	3
3	2026-02-16	2026-02-18	omo	approved	2026-02-14 22:13:27.446309+01	2026-02-14 22:03:15.034609+01	2	1	2
\.


--
-- Data for Name: loans_loanapplication; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.loans_loanapplication (id, loan_type, loan_amount, monthly_deduction, tenure_months, outstanding_balance, status, progress, applied_at, approved_at, approved_by_id, payee_id) FROM stdin;
1	personal	10000.00	2500.00	4	10000.00	approved	0.00	2026-02-05 10:42:31.847+01	2026-02-09 14:38:23.399+01	1	1
2	personal	2000.00	1000.00	2	2000.00	approved	0.00	2026-02-14 22:01:54.721704+01	2026-02-14 22:13:40.465291+01	1	2
\.


--
-- Data for Name: payroll_payrollperiod; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_payrollperiod (id, month, year, is_generated, is_locked, is_approved_by_bursar, is_approved_by_admin) FROM stdin;
1	2	2026	f	t	f	t
2	3	2026	t	t	f	t
3	1	2026	t	t	f	t
6	4	2026	t	t	f	t
7	5	2026	t	t	f	t
8	7	2026	t	t	f	t
9	8	2026	t	t	f	t
10	9	2026	t	t	f	t
11	10	2026	t	t	f	t
12	11	2026	t	t	f	t
\.


--
-- Data for Name: payroll_payrollrecord; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_payrollrecord (id, gross_pay, loan_deductions, tax_deductions, other_deductions, total_deductions, net_pay, created_at, payee_id, payroll_period_id, is_processed, processing_error) FROM stdin;
7	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-14 22:26:28.446507+01	1	6	t	\N
8	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-14 22:26:28.491336+01	2	6	t	\N
9	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-14 22:26:28.517224+01	3	6	t	\N
10	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 03:40:02.487291+01	1	7	t	\N
11	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 03:40:02.545675+01	2	7	t	\N
12	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 03:40:02.566848+01	3	7	t	\N
13	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 03:46:44.987887+01	1	8	t	\N
14	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 03:46:45.047915+01	2	8	t	\N
15	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 03:46:45.068464+01	3	8	t	\N
16	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 04:12:01.214906+01	1	9	t	\N
17	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 04:12:01.2645+01	2	9	t	\N
18	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 04:12:01.287393+01	3	9	t	\N
19	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 04:28:17.842323+01	1	10	t	\N
20	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 04:28:17.899626+01	2	10	t	\N
21	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 04:28:17.92128+01	3	10	t	\N
22	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 04:36:05.809008+01	1	11	t	\N
23	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 04:36:05.851768+01	2	11	t	\N
24	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 04:36:05.873251+01	3	11	t	\N
25	40000.00	2500.00	0.00	0.00	2500.00	37500.00	2026-02-15 04:39:14.902505+01	1	12	t	\N
26	40000.00	1000.00	0.00	0.00	1000.00	39000.00	2026-02-15 04:39:14.936173+01	2	12	t	\N
27	90000.00	0.00	0.00	20000.00	20000.00	70000.00	2026-02-15 04:39:14.957624+01	3	12	t	\N
\.


--
-- Data for Name: loans_loanrepayment; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.loans_loanrepayment (id, amount_paid, balance_after, created_at, loan_id, payroll_record_id) FROM stdin;
\.


--
-- Data for Name: payroll_auditlog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_auditlog (id, action, model_name, object_id, description, "timestamp", user_id) FROM stdin;
1	FAIL	PayrollRecord	9	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-14 22:29:25.094807+01	1
2	FAIL	PayrollRecord	12	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 03:41:58.03862+01	1
3	FAIL	PayrollRecord	12	Retry failed: You cannot initiate third party payouts as a starter business	2026-02-15 03:42:30.802036+01	1
4	FAIL	PayrollRecord	15	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 03:47:22.123598+01	1
5	FAIL	PayrollRecord	18	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 04:13:05.490689+01	1
6	FAIL	PayrollRecord	24	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 04:36:36.448897+01	1
7	FAIL	PayrollRecord	24	Retry failed: You cannot initiate third party payouts as a starter business	2026-02-15 04:37:11.165175+01	1
8	FAIL	PayrollRecord	25	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 04:39:57.56115+01	1
9	FAIL	PayrollRecord	27	Transfer failed: You cannot initiate third party payouts as a starter business	2026-02-15 04:40:00.629089+01	1
\.


--
-- Data for Name: payroll_bankaccount; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_bankaccount (id, bank_name, bank_code, account_number, account_name, recipient_code, is_primary, is_approved, payee_id) FROM stdin;
2	OPay Digital Services Limited (Paycom)	999992	8022566144	Idrees Ademola Oladimeji	RCP_tr2byn49axj5vjo	t	t	3
3	Wema Bank	035	0019304152	Gabriel Tolani Ishola		f	t	2
4	PalmPay	090115	8022566144	Idrees Ademola Oladimeji		t	t	2
1	Jaiz Bank	301	8079823665	Idrees Ademola Oladimeji		f	t	1
5	Stanbic IBTC Bank	221	0019304152	Oladimeji Idrees Ademola	RCP_j2a96fbzl9mkzc8	t	t	1
\.


--
-- Data for Name: payroll_salarystructure; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_salarystructure (id, name, description, created_at, is_taxable, tax_rate) FROM stdin;
1	Teacher Level 1	Salary for teachers in level 1	2026-02-10 21:45:01.591+01	f	0.00
2	Principal	Head of Staff	2026-02-14 22:25:29.872383+01	f	0.00
\.


--
-- Data for Name: payroll_payeesalarystructure; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_payeesalarystructure (id, assigned_at, payee_id, salary_structure_id) FROM stdin;
1	2026-02-10 21:46:33.647+01	2	1
2	2026-02-14 22:17:09.898967+01	1	1
3	2026-02-14 22:26:04.5918+01	3	2
\.


--
-- Data for Name: payroll_paymentbatch; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_paymentbatch (id, reference, total_amount, created_at, is_processed, created_by_id, payroll_period_id) FROM stdin;
1	BATCH-D97E6129	146500.00	2026-02-14 22:29:16.319465+01	t	1	6
2	BATCH-D9570862	146500.00	2026-02-15 03:41:48.743544+01	t	1	7
3	BATCH-E29153AC	146500.00	2026-02-15 03:47:16.420946+01	t	1	8
4	BATCH-AC039294	146500.00	2026-02-15 04:12:59.541845+01	t	1	9
5	BATCH-71A86AE8	146500.00	2026-02-15 04:36:30.917984+01	t	1	11
6	BATCH-D6011B73	146500.00	2026-02-15 04:39:54.51746+01	t	1	12
\.


--
-- Data for Name: payroll_paymenttransaction; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_paymenttransaction (id, amount, currency, paystack_reference, transfer_code, status, failure_reason, response_data, created_at, updated_at, batch_id, payroll_record_id) FROM stdin;
1	37500.00	NGN	PAY-7-315982		failed	Failed to create Paystack recipient	{}	2026-02-14 22:29:16.343804+01	2026-02-14 22:29:19.559311+01	1	7
2	39000.00	NGN	PAY-8-5C3566		failed	Failed to create Paystack recipient	{}	2026-02-14 22:29:19.574636+01	2026-02-14 22:29:21.955318+01	1	8
3	70000.00	NGN	PAY-9-C837A3		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business"}	2026-02-14 22:29:21.970086+01	2026-02-14 22:29:25.093217+01	1	9
4	37500.00	NGN	PAY-10-D143E1		failed	Failed to create Paystack recipient	{}	2026-02-15 03:41:48.760303+01	2026-02-15 03:41:51.685242+01	2	10
5	39000.00	NGN	PAY-11-F45B35		failed	Failed to create Paystack recipient	{}	2026-02-15 03:41:51.703424+01	2026-02-15 03:41:56.187439+01	2	11
6	70000.00	NGN	RETRY-12-10DDD3		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business", "retry": true}	2026-02-15 03:41:56.205324+01	2026-02-15 03:42:30.799856+01	2	12
7	37500.00	NGN	PAY-13-89B0DE		failed	Failed to create Paystack recipient	{}	2026-02-15 03:47:16.436797+01	2026-02-15 03:47:19.159291+01	3	13
8	39000.00	NGN	PAY-14-0A9432		failed	Failed to create Paystack recipient	{}	2026-02-15 03:47:19.184187+01	2026-02-15 03:47:20.597903+01	3	14
9	70000.00	NGN	PAY-15-386FB4		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business"}	2026-02-15 03:47:20.608237+01	2026-02-15 03:47:22.122422+01	3	15
10	37500.00	NGN	PAY-16-D67861		failed	Failed to create Paystack recipient	{}	2026-02-15 04:12:59.562703+01	2026-02-15 04:13:02.408732+01	4	16
11	39000.00	NGN	PAY-17-F07904		failed	Failed to create Paystack recipient	{}	2026-02-15 04:13:02.417838+01	2026-02-15 04:13:04.04807+01	4	17
12	70000.00	NGN	PAY-18-8E6BC4		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business"}	2026-02-15 04:13:04.05742+01	2026-02-15 04:13:05.489353+01	4	18
13	37500.00	NGN	PAY-22-B47233		failed	Failed to create Paystack recipient	{}	2026-02-15 04:36:30.934643+01	2026-02-15 04:36:33.476699+01	5	22
14	39000.00	NGN	PAY-23-CB7DEF		failed	Failed to create Paystack recipient	{}	2026-02-15 04:36:33.496408+01	2026-02-15 04:36:35.012599+01	5	23
15	70000.00	NGN	RETRY-24-F7EE35		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business", "retry": true}	2026-02-15 04:36:35.033675+01	2026-02-15 04:37:11.161798+01	5	24
16	37500.00	NGN	PAY-25-6E4200		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business"}	2026-02-15 04:39:54.534118+01	2026-02-15 04:39:57.557837+01	6	25
17	39000.00	NGN	PAY-26-DA1F3B		failed	Failed to create Paystack recipient	{}	2026-02-15 04:39:57.578324+01	2026-02-15 04:39:59.088219+01	6	26
18	70000.00	NGN	PAY-27-64DE82		failed	You cannot initiate third party payouts as a starter business	{"error": "You cannot initiate third party payouts as a starter business"}	2026-02-15 04:39:59.09487+01	2026-02-15 04:40:00.626781+01	6	27
\.


--
-- Data for Name: payroll_payrolllineitem; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_payrolllineitem (id, name, amount, is_deduction, payroll_record_id) FROM stdin;
3	Basic Salary	25000.00	f	7
4	Allowances	15000.00	f	7
5	Basic Salary	25000.00	f	8
6	Allowances	15000.00	f	8
7	Basic Salary	40000.00	f	9
8	Allowances	25000.00	f	9
9	Car Maintaince	15000.00	f	9
10	Car Loan	20000.00	t	9
11	Wardrobe Allowance	10000.00	f	9
12	Basic Salary	25000.00	f	10
13	Allowances	15000.00	f	10
14	Basic Salary	25000.00	f	11
15	Allowances	15000.00	f	11
16	Basic Salary	40000.00	f	12
17	Allowances	25000.00	f	12
18	Car Maintaince	15000.00	f	12
19	Car Loan	20000.00	t	12
20	Wardrobe Allowance	10000.00	f	12
21	Basic Salary	25000.00	f	13
22	Allowances	15000.00	f	13
23	Basic Salary	25000.00	f	14
24	Allowances	15000.00	f	14
25	Basic Salary	40000.00	f	15
26	Allowances	25000.00	f	15
27	Car Maintaince	15000.00	f	15
28	Car Loan	20000.00	t	15
29	Wardrobe Allowance	10000.00	f	15
30	Basic Salary	25000.00	f	16
31	Allowances	15000.00	f	16
32	Basic Salary	25000.00	f	17
33	Allowances	15000.00	f	17
34	Basic Salary	40000.00	f	18
35	Allowances	25000.00	f	18
36	Car Maintaince	15000.00	f	18
37	Car Loan	20000.00	t	18
38	Wardrobe Allowance	10000.00	f	18
39	Basic Salary	25000.00	f	19
40	Allowances	15000.00	f	19
41	Basic Salary	25000.00	f	20
42	Allowances	15000.00	f	20
43	Basic Salary	40000.00	f	21
44	Allowances	25000.00	f	21
45	Car Maintaince	15000.00	f	21
46	Car Loan	20000.00	t	21
47	Wardrobe Allowance	10000.00	f	21
48	Basic Salary	25000.00	f	22
49	Allowances	15000.00	f	22
50	Basic Salary	25000.00	f	23
51	Allowances	15000.00	f	23
52	Basic Salary	40000.00	f	24
53	Allowances	25000.00	f	24
54	Car Maintaince	15000.00	f	24
55	Car Loan	20000.00	t	24
56	Wardrobe Allowance	10000.00	f	24
57	Basic Salary	25000.00	f	25
58	Allowances	15000.00	f	25
59	Basic Salary	25000.00	f	26
60	Allowances	15000.00	f	26
61	Basic Salary	40000.00	f	27
62	Allowances	25000.00	f	27
63	Car Maintaince	15000.00	f	27
64	Car Loan	20000.00	t	27
65	Wardrobe Allowance	10000.00	f	27
\.


--
-- Data for Name: payroll_salarycomponent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_salarycomponent (id, name, component_type, is_active) FROM stdin;
1	Basic Salary	earning	t
2	Allowances	earning	t
3	Car Maintaince	earning	t
4	Car Loan	deduction	t
5	Wardrobe Allowance	earning	t
\.


--
-- Data for Name: payroll_salarystructureitem; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_salarystructureitem (id, amount, component_id, salary_structure_id) FROM stdin;
1	25000.00	1	1
2	15000.00	2	1
3	40000.00	1	2
4	25000.00	2	2
5	15000.00	3	2
6	20000.00	4	2
7	10000.00	5	2
\.


--
-- Data for Name: payroll_schoolsettings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payroll_schoolsettings (id, name, address, logo) FROM stdin;
\.


--
-- Data for Name: pickup_pickupauthorization; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pickup_pickupauthorization (id, reference, bearer_name, relationship, qrcode_image, expires_at, is_used, created_at, parent_id) FROM stdin;
1	be03742a-2924-4a82-a63c-0a8e442ba38a	Bearer for Harley	Uncle	pickup_qrcodes/be03742a-2924-4a82-a63c-0a8e442ba38a.png	2026-02-01 03:05:51.195+01	f	2026-01-31 16:05:51.196+01	4
2	f05956dd-167c-4a23-b1bd-a49cd4eed5d8	Bearer for 	Father	pickup_qrcodes/f05956dd-167c-4a23-b1bd-a49cd4eed5d8.png	2026-02-01 03:05:51.337+01	f	2026-01-31 16:05:51.338+01	5
3	d44e969f-cdac-49b4-a2d6-ad9a2bdb078c	Bearer for 	Uncle	pickup_qrcodes/d44e969f-cdac-49b4-a2d6-ad9a2bdb078c.png	2026-02-01 03:05:51.424+01	t	2026-01-31 16:05:51.425+01	6
4	79a41240-3a58-4957-a78b-26c88559974b	Bearer for 	Uncle	pickup_qrcodes/79a41240-3a58-4957-a78b-26c88559974b.png	2026-02-04 18:28:41.086+01	f	2026-01-31 16:05:51.547+01	7
5	f909b493-7496-42c4-afad-c10441e87d76	Bearer for 	Uncle	pickup_qrcodes/f909b493-7496-42c4-afad-c10441e87d76.png	2026-02-01 03:05:51.671+01	t	2026-01-31 16:05:51.673+01	8
6	eabb45f8-d69e-4850-9f96-384929ac1419	Tolani	Sibling	pickup_qrcodes/eabb45f8-d69e-4850-9f96-384929ac1419_xSwhN0D.png	2026-02-05 03:57:15.657+01	t	2026-02-04 16:57:15.659+01	6
7	d54eea6f-deb8-458a-9ad4-8a293c31206a	Tolani	Sibling	pickup_qrcodes/d54eea6f-deb8-458a-9ad4-8a293c31206a_8ly2LNd.png	2026-02-11 17:58:52.299+01	t	2026-02-11 06:58:52.299+01	7
\.


--
-- Data for Name: pickup_pickupstudent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pickup_pickupstudent (id, pickup_id, student_id) FROM stdin;
1	1	19
2	1	20
3	2	20
4	3	19
5	3	20
6	3	18
7	4	20
8	4	19
9	4	18
10	5	18
11	5	20
12	6	18
13	6	20
14	7	19
15	7	20
\.


--
-- Data for Name: pickup_pickupverificationlog; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pickup_pickupverificationlog (id, status, verified_at, pickup_id, verified_by_id) FROM stdin;
1	USED	2026-01-31 16:05:51.319+01	1	1
2	USED	2026-01-31 16:05:51.407+01	2	1
3	EXPIRED	2026-01-31 16:05:51.532+01	3	1
4	SUCCESS	2026-01-31 16:05:51.656+01	4	1
5	EXPIRED	2026-01-31 16:05:51.767+01	5	1
6	SUCCESS	2026-01-31 17:56:26.859+01	5	1
7	SUCCESS	2026-01-31 17:57:05.358+01	3	1
8	SUCCESS	2026-02-04 18:28:19.364+01	6	1
9	FORCE_EXPIRED	2026-02-04 18:28:41.104+01	4	1
10	SUCCESS	2026-02-11 07:01:23.867+01	7	1
\.


--
-- Name: accounts_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_user_groups_id_seq', 1, false);


--
-- Name: accounts_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_user_id_seq', 23, true);


--
-- Name: accounts_user_parents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_user_parents_id_seq', 17, true);


--
-- Name: accounts_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_user_user_permissions_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 400, true);


--
-- Name: brillspay_brillspaylog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_brillspaylog_id_seq', 9, true);


--
-- Name: brillspay_cart_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_cart_id_seq', 6, true);


--
-- Name: brillspay_cartitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_cartitem_id_seq', 18, true);


--
-- Name: brillspay_orderitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_orderitem_id_seq', 8, true);


--
-- Name: brillspay_paymenttransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_paymenttransaction_id_seq', 2, true);


--
-- Name: brillspay_productcategory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_productcategory_id_seq', 6, true);


--
-- Name: brillspay_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brillspay_transaction_id_seq', 7, true);


--
-- Name: dashboards_attempthistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_attempthistory_id_seq', 1, false);


--
-- Name: dashboards_bulkexportjob_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_bulkexportjob_id_seq', 1, false);


--
-- Name: dashboards_bulkimportjob_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_bulkimportjob_id_seq', 8, true);


--
-- Name: dashboards_certificate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_certificate_id_seq', 1, false);


--
-- Name: dashboards_certificatetemplate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_certificatetemplate_id_seq', 1, true);


--
-- Name: dashboards_chatroom_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_chatroom_id_seq', 5, true);


--
-- Name: dashboards_chatroom_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_chatroom_participants_id_seq', 11, true);


--
-- Name: dashboards_chatroommessage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_chatroommessage_id_seq', 4, true);


--
-- Name: dashboards_chatroomreadstatus_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_chatroomreadstatus_id_seq', 8, true);


--
-- Name: dashboards_examanalytics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_examanalytics_id_seq', 5, true);


--
-- Name: dashboards_examschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_examschedule_id_seq', 1, false);


--
-- Name: dashboards_gradingrubric_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_gradingrubric_id_seq', 1, false);


--
-- Name: dashboards_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_notification_id_seq', 5, true);


--
-- Name: dashboards_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_permission_id_seq', 1, false);


--
-- Name: dashboards_questionbank_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_questionbank_id_seq', 9, true);


--
-- Name: dashboards_questionbank_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_questionbank_tags_id_seq', 1, false);


--
-- Name: dashboards_questioncategory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_questioncategory_id_seq', 1, false);


--
-- Name: dashboards_questionchoice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_questionchoice_id_seq', 32, true);


--
-- Name: dashboards_questiontag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_questiontag_id_seq', 1, false);


--
-- Name: dashboards_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_role_id_seq', 1, false);


--
-- Name: dashboards_rolepermission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_rolepermission_id_seq', 1, false);


--
-- Name: dashboards_rubriccriteria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_rubriccriteria_id_seq', 1, false);


--
-- Name: dashboards_rubriccriteriagrade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_rubriccriteriagrade_id_seq', 1, false);


--
-- Name: dashboards_rubricgrade_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_rubricgrade_id_seq', 1, false);


--
-- Name: dashboards_rubricscore_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_rubricscore_id_seq', 1, false);


--
-- Name: dashboards_schedulednotification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_schedulednotification_id_seq', 1, false);


--
-- Name: dashboards_studentperformance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_studentperformance_id_seq', 1, false);


--
-- Name: dashboards_userrole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.dashboards_userrole_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 35, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 79, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 40, true);


--
-- Name: exams_broadcast_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_broadcast_id_seq', 6, true);


--
-- Name: exams_broadcast_recipients_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_broadcast_recipients_id_seq', 9, true);


--
-- Name: exams_chatmessage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_chatmessage_id_seq', 17, true);


--
-- Name: exams_choice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_choice_id_seq', 371, true);


--
-- Name: exams_exam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_exam_id_seq', 50, true);


--
-- Name: exams_examaccess_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_examaccess_id_seq', 1, true);


--
-- Name: exams_examattempt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_examattempt_id_seq', 21, true);


--
-- Name: exams_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_notification_id_seq', 57, true);


--
-- Name: exams_ptarequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_ptarequest_id_seq', 1, false);


--
-- Name: exams_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_question_id_seq', 156, true);


--
-- Name: exams_retakerequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_retakerequest_id_seq', 4, true);


--
-- Name: exams_schoolclass_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_schoolclass_id_seq', 14, true);


--
-- Name: exams_studentanswer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_studentanswer_id_seq', 51, true);


--
-- Name: exams_subject_classes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_subject_classes_id_seq', 38, true);


--
-- Name: exams_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_subject_id_seq', 12, true);


--
-- Name: exams_subjectivemark_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_subjectivemark_id_seq', 7, true);


--
-- Name: exams_systemlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_systemlog_id_seq', 87, true);


--
-- Name: leaves_leaverequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.leaves_leaverequest_id_seq', 3, true);


--
-- Name: leaves_leavetype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.leaves_leavetype_id_seq', 3, true);


--
-- Name: loans_loanapplication_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.loans_loanapplication_id_seq', 2, true);


--
-- Name: loans_loanrepayment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.loans_loanrepayment_id_seq', 1, false);


--
-- Name: payroll_auditlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_auditlog_id_seq', 9, true);


--
-- Name: payroll_bankaccount_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_bankaccount_id_seq', 5, true);


--
-- Name: payroll_payee_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_payee_id_seq', 3, true);


--
-- Name: payroll_payeesalarystructure_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_payeesalarystructure_id_seq', 3, true);


--
-- Name: payroll_paymentbatch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_paymentbatch_id_seq', 6, true);


--
-- Name: payroll_paymenttransaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_paymenttransaction_id_seq', 18, true);


--
-- Name: payroll_payrolllineitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_payrolllineitem_id_seq', 65, true);


--
-- Name: payroll_payrollperiod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_payrollperiod_id_seq', 12, true);


--
-- Name: payroll_payrollrecord_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_payrollrecord_id_seq', 27, true);


--
-- Name: payroll_salarycomponent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_salarycomponent_id_seq', 5, true);


--
-- Name: payroll_salarystructure_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_salarystructure_id_seq', 2, true);


--
-- Name: payroll_salarystructureitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_salarystructureitem_id_seq', 7, true);


--
-- Name: payroll_schoolsettings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payroll_schoolsettings_id_seq', 1, false);


--
-- Name: pickup_pickupauthorization_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pickup_pickupauthorization_id_seq', 7, true);


--
-- Name: pickup_pickupstudent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pickup_pickupstudent_id_seq', 15, true);


--
-- Name: pickup_pickupverificationlog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pickup_pickupverificationlog_id_seq', 10, true);


--
-- PostgreSQL database dump complete
--

\unrestrict M0BdozK2aG5K8JWQMySNEPHxcC13fRZIzLRaidgOg7Ryf6Ef2jAVuaCJU826V5o

