on run argv
	set inputPath to item 1 of argv
	set outputPath to item 2 of argv
	set inputFile to POSIX file inputPath as alias
	set outputFile to POSIX file outputPath
	tell application "Keynote"
		activate
		open inputFile
		repeat until (count of documents) > 0
			delay 0.5
		end repeat
		set deck to front document
		export deck to outputFile as slide images with properties {image format:PNG}
		close deck saving no
	end tell
end run
