docker build -t metalogo:v2 .
docker run -d  --expose 8050 --name metalogo -e VIRTUAL_HOST=metalogo.omicsnet.org -v "$(pwd)"/..:/code metalogo:v2 
