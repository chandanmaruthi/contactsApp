mysqldump -h localhost -u "root" "-ptestchandan123"  curious  --no-data > "sqlScripts/curious_test_sqlScript-"`date +"%d-%m-%Y-%H-%M-%S"`'.sql'
mysqldump -h localhost -u "root" "-ptestchandan123"  curious  --no-create-info --no-create-db > "sqlScripts/curious_test_sqlDumpData-"`date +"%d-%m-%Y-%H-%M-%S"`'.sql'
