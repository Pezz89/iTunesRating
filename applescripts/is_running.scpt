on run(appName)
	tell application "System Events" to (name of processes) contains appName
end run
