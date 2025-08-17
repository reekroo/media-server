.PHONY: up down restart pull logs

up:
	@echo "Run stacks"
	(cd server-stack && docker compose up -d)
	(cd logging-stack && docker compose up -d)
	(cd dashboard-stack && docker compose up -d)
	(cd proxy-stack && docker compose up -d)
	@echo "Done"
	docker ps

down:
	@echo "Stop stacks"
	(cd proxy-stack && docker compose down)
	(cd dashboard-stack && docker compose down)
	(cd logging-stack && docker compose down)
	(cd server-stack && docker compose down)

restart:
	$(MAKE) down
	$(MAKE) up

pull:
	@echo "Refresh stacks"
	(cd server-stack && docker compose pull)
	(cd logging-stack && docker compose pull)
	(cd dashboard-stack && docker compose pull)
	(cd proxy-stack && docker compose pull)