@echo off
start cmd /k "cd /d Controllers && mvn spring-boot:run"
start cmd /k "cd /d Frontend\trasy-dashboard && npm start"
start cmd /k "influxd"
