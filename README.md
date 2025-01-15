# GameShop-Cloud

The project contains 5 microservices:
- auth for autentification
- games for the game listing and management
- reviews for user submited reviews
- library for the user games
- frontend which offers an interface for the user and forwards HTTP request to the first 4 services

Each service is run in it's own docker container and has it's own postgres database (check docker-compose.yaml for more info).
