default: autocommit

autocommit:
	# now=$(date +"%T")
	git add -A
	# git commit -m "Auto Commit: $(now)"
	git commit -m "Auto Commit"
	git push git@github.com:alisaad05/utils master