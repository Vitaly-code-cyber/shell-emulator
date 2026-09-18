# Этап 5: все режимы команды chmod на образе deep.
# Ошибочная команда стоит последней: выполнение скрипта
# прекращается на первой ошибке.
ls -l /home/user
echo --- восьмеричный режим ---
chmod 600 /home/user/profile.conf
ls -l /home/user
echo --- символьный режим: добавление права ---
chmod u+x /home/user/profile.conf
ls -l /home/user
echo --- символьный режим: снятие права ---
chmod a-w /home/user/profile.conf
ls -l /home/user
echo --- несколько правил через запятую ---
chmod u=rw,go=r /home/user/profile.conf
ls -l /home/user
echo --- права каталога и нескольких путей сразу ---
chmod 750 /home/user/docs /home/user/images
ls -l /home/user
echo --- ошибка: неверная запись режима ---
chmod 999 /home/user/profile.conf
exit
