app="tabletop.docker"
docker build -t ${app} .
docker run -ti -p 56733:80 --name=${app} tabletop
