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

test:
	python bot.py CheckAvailability PokeStats -d 5
	python bot.py CheckAvailability PokeApi -d 5
	python bot.py CheckAvailability PokeImages -d 5
	python bot.py CheckAvailability PokeSearch -d 5

	python bot.py CheckLatency PokeStats --start-date 10/10/2023 --end-date 14/10/2023
	python bot.py CheckLatency PokeApi --start-date 10/10/2023 --end-date 14/10/2023
	python bot.py CheckLatency PokeImages --start-date 10/10/2023 --end-date 14/10/2023
	python bot.py CheckLatency PokeSearch --start-date 10/10/2023 --end-date 14/10/2023	

	python bot.py RenderGraph PokeStats --graph-type Latency -d 12
	python bot.py RenderGraph PokeApi --graph-type Latency -d 12
	python bot.py RenderGraph PokeImages --graph-type Latency -d 12
	python bot.py RenderGraph PokeSearch --graph-type Latency -d 12

	python bot.py RenderGraph PokeStats --graph-type Availability -d 12
	python bot.py RenderGraph PokeApi --graph-type Availability -d 12
	python bot.py RenderGraph PokeImages --graph-type Availability -d 12
	python bot.py RenderGraph PokeSearch --graph-type Availability -d 12