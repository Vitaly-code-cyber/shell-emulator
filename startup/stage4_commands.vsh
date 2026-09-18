# Этап 4: все режимы команд ls, cd, history и echo на образе deep.
# Ошибочная команда стоит последней, так как выполнение скрипта
# прекращается на первой ошибке.
ls
ls -l
ls /home/user
ls -l /home/user/docs
ls /home/user/profile.conf
cd home
cd user/docs
ls -l
cd ..
ls
cd ../..
ls -l /etc/app
echo Проверка команды echo
echo
history
history 3
ls /home/nobody
exit
