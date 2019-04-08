build_test_index:
	docker-compose exec web /code/bin/scrapper.py --output-dir /code/data/mails-html/ -t 5 --debug --years 2018 --months April
	docker-compose exec web /code/bin/parser.py --input-dir /code/data/mails-html/ --output-dir /code//data/mails-json
	docker-compose exec web /code/bin/index.py --input-mails /code/data/mails-json/ --out-index /code/data/index/  --ram 512 --procs 8

build_index:
	docker-compose exec web /code/bin/scrapper.py --output-dir /code/data/mails-html/ -t 5
	docker-compose exec web /code/bin/parser.py --input-dir /code/data/mails-html/ --output-dir /code//data/mails-json
	docker-compose exec web /code/bin/index.py --input-mails /code/data/mails-json/ --out-index /code/data/index/  --ram 512 --procs 8

up:
	docker-compose -p pyscar up

start:
	docker-compose start
