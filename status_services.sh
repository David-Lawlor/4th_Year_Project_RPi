#!/bin/bash
systemctl daemon-reload
systemctl status aws_temperature_sensor.service
systemctl status aws_temperature_humidity_sensor.service
systemctl status aws_light_sensor.service
systemctl status aws_pi_stats.service
systemctl status aws_pi_device_shadow.service
