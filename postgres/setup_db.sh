#Setup PostgreSQL DB on Docker container (persistent data)
mkdir -p $HOME/docker/volumes/postgres

docker run --rm --name pg-docker \
           -e POSTGRES_PASSWORD=postgrespassword \
           -d -p 127.0.0.1:5432:5432 \
           -v $HOME/docker/volumes/postgres:/var/lib/postgresql/data postgres

#To connect to PG without installing it on the current instance, run:
#docker exec --tty --interactive pg-docker psql -h localhost -U postgres -d postgres

#Create login user and install phppg_admin
docker exec --tty --interactive pg-docker /bin/bash
su -c "psql -c \"CREATE USER postgresuser WITH LOGIN PASSWORD 'postgrespassword';\"" postgres

