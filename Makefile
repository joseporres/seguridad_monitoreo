seed:
	docker-compose exec poke_stats make seed

backup:
	docker exec -it mongodb-seguridad-monitoreo mongodump --archive=./backup.gz -u root -p root
	docker cp mongodb-seguridad-monitoreo:./backup.gz ./backup.gz

clean:
	docker exec -it mongodb-seguridad-monitoreo mongo -u root -p root --eval "use seguridad-monitoreo; db.dropDatabase();"
	
restore:
	docker cp ./backup.gz mongodb-seguridad-monitoreo:./backup.gz
	docker exec -it mongodb-seguridad-monitoreo mongorestore --archive=./backup.gz -u root -p root