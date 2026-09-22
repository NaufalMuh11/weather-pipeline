CREATE USER superset WITH PASSWORD 'superset' CREATEDB;
CREATE DATABASE superset_db OWNER superset;
CREATE USER examples WITH PASSWORD 'examples' CREATEDB;
CREATE DATABASE examples_db OWNER examples;