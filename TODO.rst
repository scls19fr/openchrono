Arduino
	make a for loop over ADC channels
	speedup data sending
	measure ellapsed time using millis()

Raspberry Side
	speedup data receive
	save to memory and to file (or to database)
	create GUI to calibrate ADC

create Arduino code, compile and send from Python
	using template (Jinja)

Linux package requirements
	Raspbian packages
		python ou python3
		arduino
		arduino-mk

Logging
	use a config file for logger


Install
	sudo python setup.py install

Scripts
	python scripts/console.py

Uninstall
	sudo pip uninstall openchrono
