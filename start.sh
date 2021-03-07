docker build --tag ingestor:latest ./ingestor
docker build --tag pg-to-aws:latest ./pg-to-aws

pgpwd="$(cat conf.json | python3 -c "import sys,json; print(json.load(sys.stdin)['secrets']['POSTGRES_PWD'])")"
pgusr="$(cat conf.json | python3 -c "import sys,json; print(json.load(sys.stdin)['POSTGRES_USR'])")"
pghost="$(cat conf.json | python3 -c "import sys,json; print(json.load(sys.stdin)['POSTGRES_HOST'])")"

docker network create pg-net
docker run -d --network pg-net --network-alias "${pghost}" -e POSTGRES_PASSWORD="${pgpwd}" -e POSTGRES_USER="${pgusr}" --name pg-staging postgres

sleep 5

docker run --rm --network pg-net -v "${PWD}/conf.json":/code/conf.json ingestor:latest
docker run --rm --network pg-net -v "${PWD}/conf.json":/code/conf.json -v "${PWD}/data":/code/data pg-to-aws:latest

docker rm -f pg-staging
docker network rm pg-net
