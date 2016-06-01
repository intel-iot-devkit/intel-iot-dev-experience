config_sensor = {
    broker: {
		host:    'test.mosquitto.org',
		wssPort: 8081,
		wsPort:  8080,
		topic: "/sensors",
		reconnectTimeout: 5000,
		reconnectInterval: 3
    }
};