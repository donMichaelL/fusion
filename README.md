# Push
* docker build -t donmichael/fusion_adapter . 
* docker push donmichael/fusion_adapter

# Deploy/update docker stack
docker stack deploy -c docker-compose.yml fusion



------------------------------------------------------------------

# check stack's status
docker stack ps fusion

# Check logs of a service 
docker service logs  --follow fusion_adapter

# delete a stack
docker stack rm fusion
