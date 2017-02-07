#!/bin/bash
systemctl daemon-reload
systemctl disable aws_temperature_sensor.service
systemctl disable aws_temperature_humidity_sensor.service
systemctl disable aws_light_sensor.service
systemctl disable aws_pi_stats.service
systemctl disable aws_pi_device_shadow.service
