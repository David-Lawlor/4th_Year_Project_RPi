#!/bin/bash
systemctl daemon-reload
systemctl enable aws_temperature_sensor.service
systemctl enable aws_temperature_humidity_sensor.service
systemctl enable aws_light_sensor.service
systemctl enable aws_pi_stats.service
systemctl enable aws_pi_device_shadow.service
