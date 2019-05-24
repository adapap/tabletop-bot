app="tabletop:1.0"
docker build -t ${app} .
docker run -d --name Tabletop ${app}
