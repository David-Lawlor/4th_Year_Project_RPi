#!/bin/bash
systemctl daemon-reload
systemctl stop aws_temperature_sensor.service
systemctl stop aws_temperature_humidity_sensor.service
systemctl stop aws_light_sensor.service
systemctl stop aws_pi_stats.service
systemctl stop aws_pi_device_shadow.service
