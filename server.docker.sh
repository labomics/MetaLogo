docker build -t metalogo:v1 .
docker run -d  --expose 8050 --name metalogo -e VIRTUAL_HOST=metalogo.omicsnet.org -v .:/code metalogo:v1 
