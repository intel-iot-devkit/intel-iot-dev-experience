config_sensor = {
    broker: {
		host:    null, // was window.location.hostname, but set from $scope.device wan ip address (see $scope.mqttInit in app.js)
		wssPort: 9002,
		wsPort:  9001, 
		topic: "/sensors",
		reconnectTimeout: 5000,
		reconnectInterval: 3
    },
    charts: [
	{
	    title: "Temperature",
	    chartType: "line",
	    units: "F",
	    min: "0",
	    max: "100",
	    targetLow: "30",
	    targetHigh: "60",
	    points: "50"
	},
	{
	    title: "Humidity",
	    chartType: "gauge",
	    units: "%",
	    min: "0",
	    max: "100",
	    targetLow: "30",
	    targetHigh: "60",
	    points: "1"
	}
    ]
};
