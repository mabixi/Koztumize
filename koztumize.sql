CREATE SERVER multicorn_git FOREIGN DATA WRAPPER multicorn
options (                           
 wrapper 'multicorn.gitfdw.GitFdw'
);


CREATE FOREIGN TABLE GitCommit (
    "author_name" character varying,
    "author_email" character varying,
    "message" character varying,
    "hash" character varying,
    "date" timestamp) SERVER multicorn_git
OPTIONS (path 'path_to/archive.git');

