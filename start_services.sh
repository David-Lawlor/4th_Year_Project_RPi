#!/bin/bash
systemctl daemon-reload
systemctl start aws_temperature_sensor.service
systemctl start aws_temperature_humidity_sensor.service
systemctl start aws_light_sensor.service
systemctl start aws_pi_stats.service
systemctl start aws_pi_device_shadow.service
