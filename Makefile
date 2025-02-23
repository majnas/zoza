COMPOSE_FILE_PATH := -f docker-compose.yml
PN=zoza

# Another way using a target
include .env
export $(shell sed 's/=.*//' .env)


vars:
	@env


# init:	
# 	@echo "\e[1;93m\n[Init] >> Set permissions for all subfolders ... \e[0m"
# 	# Recursively set permissions for all subfolders in the services directory
	
# 	sudo chmod -R o+rw $(ROOT_SERVICES);
# 	sudo chmod -R o+rw $(SERVICES_DATA);

db:
	$(info Make: Downing, ReBuilding "$(TARGET_DEPLOY_TYPE)" environment images.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) down
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) build

dbu:
	$(info Make: Downing, ReBuilding and Upping "$(TARGET_DEPLOY_TYPE)" environment images.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) down
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) build
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) up

dbud:
	$(info Make: Downing, REBuilding and Upping in back "$(TARGET_DEPLOY_TYPE)" environment images.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) down
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) build
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) up -d

ps:
	$(info FILES: $(COMPOSE_FILE_PATH))
	$(info Make: Listing containers "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) ps

upd:
	$(info Make: Upping "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) up -d

up:
	$(info Make: Upping "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) up	

start:
	$(info Make: Starting "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) up -d

stop:
	$(info Make: Stopping "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) stop

down:
	$(info Make: Stopping "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) down

restart:
	$(info Make: Restarting "$(TARGET_DEPLOY_TYPE)" environment containers.)
	@make -s stop
	@make -s start
	@make -s logs

logs:
	$(info Make: Logs "$(TARGET_DEPLOY_TYPE)" environment containers.)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) logs -f -t --tail 10

config:
	$(info Make: config "$(TARGET_DEPLOY_TYPE)" for solution "$(SOL_NAME)".)
	docker compose --project-name $(PN) $(COMPOSE_FILE_PATH) config

# test-text-to-image:
test-image-to-text:
	docker exec -it image_to_text_$(SOL_SUFFIX) sh -c 'cd /srv/image_to_text && sh run_tests.sh'
